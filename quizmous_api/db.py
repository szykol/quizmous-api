import asyncio
import asyncpg

from .api.swagger.models.quiz import Quiz
from .api.swagger.models.question import Question
from .api.swagger.models.answer import Answer
from .api.swagger.models.get_user import GetUser

from itertools import chain

class DB:
    _pool: asyncpg.pool.Pool = None

    @staticmethod
    async def init(dsn, *args, **kwargs):
        DB._pool = await asyncpg.create_pool(dsn=dsn, *args, **kwargs)

    @staticmethod
    def get_pool() -> asyncpg.pool.Pool:
        return DB._pool

async def select_model_from_db(model_cls, id: int = None):
    if model_cls == Quiz:
        return await select_quiz_from_db(id)
    if model_cls == Question:
        return await select_question_from_db(id)
    if model_cls == Answer:
        return await select_answer_from_db(id)
    else:
        raise ValueError("Fetching {} model from db not supported!".format(str(model_cls)))

async def insert_model_to_db(model, id: int = None):
    if type(model) == Quiz:
        return await insert_quiz_to_db(model)
    if type(model) == Question:
        return await insert_question_to_db(model, id)
    if type(model) == Answer:
        return await insert_answer_to_db(model, id)
    else:
        raise ValueError("Fetching {} model from db not supported!".format(str(type(model))))

def get_data_for_query(model_cls):
    if model_cls == Quiz:
        return {
            "remove_keys": ['questions'],
            "id_column_name": 'quiz_id',
            "table_name": 'quiz',
            "no_parent": True
        }
    if model_cls == Question:
        return {
            "remove_keys": ['answers'],
            "id_column_name": 'quiz_id',
            "table_name": 'quiz_question'
        }
    if model_cls == Answer:
        return {
            "remove_keys": [],
            "id_column_name": 'question_id',
            "table_name": 'quiz_answer'
        }

def prepare_select_sql(model_cls, id: int = None):
    q = """ SELECT {} FROM {}""" 
    query_data = get_data_for_query(model_cls)

    model_keys = {key for key, val in model_cls.__dict__.items() if isinstance(val, property) if key not in query_data["remove_keys"]}
    column_names = ",".join(model_keys)

    q = q.format(column_names, query_data["table_name"])
    if id:
        q += ' WHERE {}=$1'.format(query_data["id_column_name"])

    return q

def prepare_insert_sql(model):
    q = """ INSERT INTO {} ({}) VALUES ({}) RETURNING *"""
    
    model_dict = model.to_dict()
    query_data = get_data_for_query(type(model))

    keys = [key for key in model_dict.keys() if "id" not in key and key not in query_data["remove_keys"]]
    # additional_key_values = ((key, val) for key, val in additional.items()) if additional else ()
    # key_values = chain(key_values, additional_key_values

    if not "no_parent" in query_data:
        keys.append(query_data['id_column_name'])

    # keys, values = zip(*key_values)
    keys = sorted(keys)
    val_indices = ('${}'.format(idx) for idx, val in enumerate(keys, 1))

    return q.format(query_data["table_name"], ','.join(keys), ','.join(val_indices)), keys

async def perform_select_sql(model_cls, id: int = None):
    query = prepare_select_sql(model_cls, id)
    if id:
        return await DB.get_pool().fetch(query, id)
    else:
        return await DB.get_pool().fetch(query)

async def select_quiz_from_db(id: int = None):
    records = await perform_select_sql(Quiz, id)
    quiz_dict = [dict(r) for r in records]
    for q in quiz_dict:
        author = await DB.get_pool().fetch(""" SELECT user_id, nick from users WHERE user_id=$1 """, q["author"])
        q["author"] = dict(author[0])

    quizes = [Quiz.from_dict(q) for q in quiz_dict]
    for quiz in quizes:
        quiz.questions = await select_question_from_db(quiz.quiz_id)
    return quizes

async def select_question_from_db(quiz_id: int = None):
    records = await perform_select_sql(Question, quiz_id)

    questions = [Question.from_dict(dict(r)) for r in records]
    for question in questions:
        question.answers = await select_answer_from_db(question.question_id)

    return questions

async def select_answer_from_db(question_id: int = None):
    records = await perform_select_sql(Answer, question_id)

    answers = [Answer.from_dict(dict(r)) for r in records]

    return answers

async def insert_quiz_to_db(quiz):
    insert_query, keys = prepare_insert_sql(quiz)

    quiz_dict = quiz.to_dict()
    quiz_dict["author"] = quiz.author.user_id

    values = (quiz_dict[key] for key in sorted(keys))
    # print('values: {} query: {}'.format(, insert_query))
    record = await DB.get_pool().fetch(insert_query, *values)
    quiz_id = record[0]["quiz_id"]
    for question in quiz.questions:
        await insert_question_to_db(question, quiz_id)

    return quiz_id

async def insert_question_to_db(question, quiz_id: int):
    insert_query, keys = prepare_insert_sql(question)

    question_dict = question.to_dict()
    question_dict["quiz_id"] = quiz_id
    values = (question_dict[key] for key in sorted(keys))
    
    record = await DB.get_pool().fetch(insert_query, *values)
    question_id = record[0]["question_id"]
    for answer in question.answers:
        await insert_answer_to_db(answer, question_id)

    return question_id

async def insert_answer_to_db(answer, question_id: int):
    insert_query, keys = prepare_insert_sql(answer)

    answer_dict = answer.to_dict()
    answer_dict["question_id"] = question_id
    values = (answer_dict[key] for key in sorted(keys))

    record = await DB.get_pool().fetch(insert_query, *values)

    return record[0]["answer_id"]