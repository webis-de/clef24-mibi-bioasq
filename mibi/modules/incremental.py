from enum import Enum
from warnings import warn
from dspy import Module, Signature, Predict, InputField, OutputField
from mibi.builder import AnswerBuilder
from mibi.model import Question, Answer
from mibi.modules import AnswerModule, DocumentsModule, SnippetsModule, ExactAnswerModule, IdealAnswerModule


class Task(Enum):
    make_documents = 'retrieve documents'
    make_snippets = 'retrieve snippets'
    make_exact_answer = 'generate exact answer'
    make_ideal_answer = 'generate summary answer'


class PredictNextTask(Signature):
    """
    Chose the next task to run, in order to get the full answer.
    """
    has_documents: bool = InputField(
        prefix="Has retrieved documents:",
        desc="If documents were already retrieved for the question."
    )
    has_snippets: bool = InputField(
        prefix="Has retrieved snippets:",
        desc="If snippets were already retrieved for the question."
    )
    has_exact_answer: bool = InputField(
        prefix="Has generated exact answer:",
        desc="If an exact answer was already generated for the question."
    )
    has_ideal_answer: bool = InputField(
        prefix="Has generated summary answer:",
        desc="If a human summary answer was already generated for the question."
    )
    task: Task = OutputField(
        desc=(
            f"Must always be one of '{Task.make_documents}', "
            f"'{Task.make_snippets}', '{Task.make_exact_answer}', or "
            f"'{Task.make_ideal_answer}'."
        ),
        prefix="Next task:",
    )


class IncrementalAnswerModule(Module, AnswerModule):
    """
    Incrementally build the full answer by asking the LLM which
    part of the answer (i.e., documents, snippets, exact answer,
    or ideal answer) to make next.
    """
    
    _documents_module: DocumentsModule
    _snippets_module: SnippetsModule
    _exact_answer_module: ExactAnswerModule
    _ideal_answer_module: IdealAnswerModule
    _next_task = Predict(signature=PredictNextTask)

    def __init__(
        self,
        documents_module: DocumentsModule,
        snippets_module: SnippetsModule,
        exact_answer_module: ExactAnswerModule,
        ideal_answer_module: IdealAnswerModule,
    ) -> None:
        self._documents_module = documents_module
        self._snippets_module = snippets_module
        self._exact_answer_module = exact_answer_module
        self._ideal_answer_module = ideal_answer_module

    def forward(self, question: Question) -> Answer:
        builder = AnswerBuilder(
            question=question,
            documents_module=self._documents_module,
            snippets_module=self._snippets_module,
            exact_answer_module=self._exact_answer_module,
            ideal_answer_module=self._ideal_answer_module,
        )
        while not builder.is_ready:
            current_answer = builder.partial_answer
            next_task = self._next_task(
                has_documents=current_answer.documents is not None,
                has_snippets=current_answer.snippets is not None,
                has_exact_answer=current_answer.exact_answer is not None,
                has_ideal_answer=current_answer.ideal_answer is not None,
            ).answer
            if next_task == Task.make_documents:
                builder.make_documents()
            if next_task == Task.make_snippets:
                builder.make_snippets()
            if next_task == Task.make_exact_answer:
                builder.make_exact_answer()
            if next_task == Task.make_ideal_answer:
                builder.make_ideal_answer()
            else:
                warn(RuntimeWarning(
                    f"Could not parse next task: {next_task!r}"
                ))
        return builder.answer
