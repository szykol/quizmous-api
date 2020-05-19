import asyncio
import asyncpg

from quizmous_api import Question, QuestionType, Answer, GetUser, PostUser, Quiz

from itertools import chain

from asyncpg.exceptions import UniqueViolationError

class UniqueModelConstraint(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg

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
    if model_cls == GetUser:
        return await select_user_from_db(id)
    else:
        raise ValueError("Fetching {} model from db not supported!".format(str(model_cls)))

async def insert_model_to_db(model, id: int = None):
    if type(model) == Quiz:
        return await insert_quiz_to_db(model)
    if type(model) == Question:
        return await insert_question_to_db(model, id)
    if type(model) == Answer:
        return await insert_answer_to_db(model, id)
    if type(model) == PostUser:
        return await insert_user_to_db(model)
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
    if model_cls == GetUser or model_cls == PostUser:
        return {
            "table_name": "users",
            "id_column_name": 'user_id',
            "remove_keys": [],
            "no_parent": True
        }

    return {}

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
    try:
        record = await DB.get_pool().fetch(insert_query, *values)
    except UniqueViolationError:
        raise UniqueModelConstraint(msg="Quiz '{}' already exists".format(quiz.name))

    quiz_id = record[0]["quiz_id"]
    for question in quiz.questions:
        await insert_question_to_db(question, quiz_id)

    return quiz_id

async def insert_question_to_db(question, quiz_id: int):
    insert_query, keys = prepare_insert_sql(question)

    question_dict = question.to_dict()
    question_dict["quiz_id"] = quiz_id
    values = (question_dict[key] for key in sorted(keys))
    
    try:
        record = await DB.get_pool().fetch(insert_query, *values)
    except UniqueViolationError:
        raise UniqueModelConstraint(msg="Question '{}' already exists for that quiz".format(question.question))

    question_id = record[0]["question_id"]
    for answer in question.answers:
        await insert_answer_to_db(answer, question_id)

    return question_id

async def insert_answer_to_db(answer, question_id: int):
    insert_query, keys = prepare_insert_sql(answer)

    answer_dict = answer.to_dict()
    answer_dict["question_id"] = question_id
    values = (answer_dict[key] for key in sorted(keys))
    try:
        record = await DB.get_pool().fetch(insert_query, *values)
    except UniqueViolationError:
        raise UniqueModelConstraint(msg="Answer '{}' already exists for that question".format(answer.answer))
    return record[0]["answer_id"]

async def insert_user_to_db(user):
    insert_query, keys = prepare_insert_sql(user)

    user_dict = user.to_dict()

    values = (user_dict[key] for key in sorted(keys))
    try:
        record = await DB.get_pool().fetch(insert_query, *values)
    except UniqueViolationError:
        raise UniqueModelConstraint(msg="User '{}' already exists".format(user.nick))
    return record[0]["user_id"]

async def insert_user_answers_to_db(answers, quiz_id):
    answer_key = answers["key"]
    answers = filter(lambda item: item[0].isdigit(), answers.items())
    query = "INSERT INTO quiz_key (quiz_id, key) VALUES ($1, $2) RETURNING key_id";
    key_id = await DB.get_pool().fetchrow(query, quiz_id, answer_key)
    key_id = key_id["key_id"]
    query = "INSERT INTO quiz_user_answers (key_id, question_id, answer_id, value) VALUES ($1, $2, $3, $4)"
    for question_id, answer in answers:
        if isinstance(answer["answer_id"], list):
            for ans in answer["answer_id"]:
                await DB.get_pool().execute(query, key_id, int(question_id), ans, answer["value"])
        else:
            await DB.get_pool().execute(query, key_id, int(question_id), answer["answer_id"], answer["value"])


async def insert_user_quiz_taken(user, id):
    q = "SELECT user_id FROM users WHERE nick=$1"
    user_id = await DB.get_pool().fetchrow(q, user.nick)
    user_id = user_id["user_id"]

    query = "INSERT INTO user_quiz_taken (quiz_id, user_id) VALUES ($1, $2)"
    await DB.get_pool().execute(query, id, user_id)

async def select_user_quiz_taken(user_nick, id):
    q = "SELECT user_id FROM users WHERE nick=$1"
    user_id = await DB.get_pool().fetchrow(q, user_nick)
    user_id = user_id["user_id"]

    query = "SELECT 1 FROM user_quiz_taken WHERE quiz_id=$1 AND user_id=$2"
    return await DB.get_pool().fetchrow(query, id, user_id)

async def select_user_from_db(id: int):
    user = dict(await perform_select_sql(GetUser, id))

    return GetUser.from_dict(user)