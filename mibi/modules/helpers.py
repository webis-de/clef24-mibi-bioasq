from abc import abstractmethod
from mibi.model import Question, PartialAnswer, ExactAnswer, YesNoExactAnswer, FactoidExactAnswer, ListExactAnswer, SummaryExactAnswer, NOT_AVAILABLE
from mibi.modules import ABCModule, ExactAnswerModule


class AutoExactAnswerModule(ExactAnswerModule, ABCModule):
    def forward(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> ExactAnswer:
        if question.type == "yesno":
            return self.forward_yes_no(question, partial_answer)
        elif question.type == "factoid":
            return self.forward_factoid(question, partial_answer)
        elif question.type == "list":
            return self.forward_list(question, partial_answer)
        elif question.type == "summary":
            return self.forward_summary(question, partial_answer)
        else:
            raise ValueError(f"Unknown question type: {question.type}")

    @abstractmethod
    def forward_yes_no(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> YesNoExactAnswer:
        raise NotImplementedError()

    @abstractmethod
    def forward_factoid(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> FactoidExactAnswer:
        raise NotImplementedError()

    @abstractmethod
    def forward_list(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> ListExactAnswer:
        raise NotImplementedError()

    def forward_summary(
        self,
        question: Question,
        partial_answer: PartialAnswer,
    ) -> SummaryExactAnswer:
        return NOT_AVAILABLE
