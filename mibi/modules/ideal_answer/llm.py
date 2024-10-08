from typing import Annotated, TypeAlias, cast
from typing_extensions import TypedDict
from warnings import warn
from dspy import Signature, Prediction, InputField, OutputField, TypedPredictor
from pydantic import Field

from mibi.model import PartiallyAnsweredQuestion, Question, PartialAnswer, IdealAnswer
from mibi.modules import IdealAnswerModule


Context: TypeAlias = list[str]


class IdealInput(TypedDict):
    question: Annotated[
        str,
        Field(
            description="The question that should be answered.",
        ),
    ]
    context: Annotated[
        Context,
        Field(
            description="Context that should be used to answer the question.",
        ),
    ]


class IdealOutput(TypedDict):
    answer: Annotated[
        str,
        Field(
            description="The long-form answer to the question consisting of 1 to 3 sentence that also contains a short explanation. The answer should be grammatically correct, concise, and precise.",
        ),
    ]


class IdealPredict(Signature):
    """Answer the medical question based on the given context (from a relevant medical abstract), basic medical knowledge, and current standard practices from medical guidelines. The answer should be based mostly on the given context if it is factually correct."""
    input: IdealInput = InputField()
    output: IdealOutput = OutputField()


class LlmIdealAnswerModule(IdealAnswerModule):
    _ideal_predict: TypedPredictor

    def __init__(self) -> None:
        self._ideal_predict = TypedPredictor(
            signature=IdealPredict,
            max_retries=3,
        )

    def _context(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> Context:
        partially_answered_question = PartiallyAnsweredQuestion.from_question(
            question, partial_answer)

        context = []

        if partially_answered_question.exact_answer_text is not None:
            context += [partially_answered_question.exact_answer_text]
        if partially_answered_question.ideal_answer is not None:
            context += [partially_answered_question.ideal_answer]
        if partially_answered_question.snippets is not None:
            context += [
                snippet.text
                for snippet in partially_answered_question.snippets
            ]
        # TODO: Extract context from document.
        return context

    def forward(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> IdealAnswer:
        input = IdealInput(
            question=question.body,
            context=self._context(question, partial_answer)
        )
        try:
            prediction: Prediction = self._ideal_predict.forward(input=input)
        except ValueError as e:
            warn(RuntimeWarning(
                f"Could not find ideal answer to question: {question.body}", e))
            warn("Falling back to empty answer.")
            return ""
        output = cast(IdealOutput, prediction.output)
        # TODO: Additional validations using DSPy assertions?
        return output["answer"]
