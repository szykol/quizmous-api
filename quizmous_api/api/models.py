from .swagger.models.answer import Answer as SwaggerAnswer
from .swagger.models.question import Question as SwaggerQuestion
from .swagger.models.quiz import Quiz as SwaggerQuiz

class Answer(SwaggerAnswer):
    pass

class Question(SwaggerQuestion):
    pass

class Quiz(SwaggerQuiz):
    pass