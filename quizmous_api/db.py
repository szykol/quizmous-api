import asyncio
import asyncpg

from quizmous_api import Question, QuestionType, Answer, GetUser, PostUser, Quiz

from itertools import chain

from asyncpg.exceptions import UniqueViolationError

class UniqueModelConstraint(Exception):
    """Exception that gets raised when model that is inserted and should be unique to the DB is already there"""
    def __init__(self, msg: str):
        """Creates new UniqueModelConstraint exception
        :param msg: error message 
        :type msg: str
        """

        self.msg = msg

    def __str__(self) -> str:
        """Returns string representation of the exception
        :return: string representation.  
        :rtype: str
        """
        return self.msg

class DB:
    """DB - PostgreSQL database wrapper"""
    _pool: asyncpg.pool.Pool = None

    @staticmethod
    async def init(dsn, *args, **kwargs):
        """Initializes the database connection pool

        :param dsn: dsn connection string 
        :type dsn: str
        """
        DB._pool = await asyncpg.create_pool(dsn=dsn, *args, **kwargs)

    @staticmethod
    def get_pool() -> asyncpg.pool.Pool:
        """Returns the database connection pool

        :return: database connection pool
        :rtype: asyncpg.pool.Pool
        """
        return DB._pool

async def select_model_from_db(model_cls, id: int = None):
    """Selects model from the database

    :param model_cls: class literal of model
    :type model_cls: class literal
    :param id: optional id of selected model, defaults to None
    :type id: int 
    :raises ValueError: Gets raised when model is not supported by that function
    :return: model object created using model_cls class literal
    :rtype: Model
    """
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
    """Inserts model to database

    :param model: Model object to insert
    :type Model: Model object
    :param id: optional id of inserted model, defaults to None
    :type id: int 
    :raises ValueError: Gets raised when model is not supported by that function
    :return: id of inserted model
    :rtype: int
    """
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
    """Returns data needed to build db query

    :param model_cls: Model used in query
    :type model_cls: model class literal
    :return: data needed to build db query
    :rtype: dict
    """
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
    """Returns select sql query for specific model

    :param model_cls: Model used in query
    :type model_cls: model class literal
    :param id: optional id of inserted model, defaults to None
    :type id: int 
    :return: select sql query
    :rtype: str
    """

    q = """ SELECT {} FROM {}""" 
    query_data = get_data_for_query(model_cls)

    model_keys = {key for key, val in model_cls.__dict__.items() if isinstance(val, property) if key not in query_data["remove_keys"]}
    column_names = ",".join(model_keys)

    q = q.format(column_names, query_data["table_name"])
    if id:
        q += ' WHERE {}=$1'.format(query_data["id_column_name"])

    return q

def prepare_insert_sql(model):
    """Returns insert sql query for specific model

    :param model: Model used in query
    :type model_cls: model object
    :return: insert sql query
    :rtype: str
    """

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
    """Performs select query

    :param model_cls: model to select
    :type model_cls: model class literal
    :param id: id of selected model, defaults to None
    :type id: int, optional
    :return: rows of data
    :rtype: Row
    """
    query = prepare_select_sql(model_cls, id)
    if id:
        return await DB.get_pool().fetch(query, id)
    else:
        return await DB.get_pool().fetch(query)

async def select_quiz_from_db(id: int = None):
    """Performs select quiz from db

    :param id: id of selected model, defaults to None
    :type id: int, optional
    :return: rows of data
    :rtype: Row
    """

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
    """Performs select question from db

    :param id: id of selected model, defaults to None
    :type id: int, optional
    :return: rows of data
    :rtype: Row
    """
    records = await perform_select_sql(Question, quiz_id)

    questions = [Question.from_dict(dict(r)) for r in records]
    for question in questions:
        question.answers = await select_answer_from_db(question.question_id)

    return questions

async def select_answer_from_db(question_id: int = None):
    """Performs select answer from db

    :param id: id of selected model, defaults to None
    :type id: int, optional
    :return: rows of data
    :rtype: Row
    """
    records = await perform_select_sql(Answer, question_id)

    answers = [Answer.from_dict(dict(r)) for r in records]

    return answers

async def insert_quiz_to_db(quiz):
    """Inserts quiz to db
    """
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
    """Inserts question to db

    :param quiz_id: id of parent quiz model
    :type quiz_id: int
    """
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
    """Inserts answer to db
    
    :param question_id: id of parent question model
    :type question_id: int
    """
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
    """Inserts user to db

    :param user: user to insert
    :type user: User model
    :raises UniqueModelConstraint: Gets raised when user already exists
    :return: id of user
    :rtype: int
    """
    insert_query, keys = prepare_insert_sql(user)

    user_dict = user.to_dict()

    values = (user_dict[key] for key in sorted(keys))
    try:
        record = await DB.get_pool().fetch(insert_query, *values)
    except UniqueViolationError:
        raise UniqueModelConstraint(msg="User '{}' already exists".format(user.nick))
    return record[0]["user_id"]

async def insert_user_answers_to_db(answers, quiz_id):
    """Inserts user answers to db

    :param answers: List of answers from user
    :type answers: List[Answer]
    :param quiz_id: Id of quiz
    :type quiz_id: int
    """
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
    """Sets the flag that user has taken the quiz

    :param user: which user taken the quiz
    :type user: User model
    :param id: Id of user
    :type id: int
    """
    q = "SELECT user_id FROM users WHERE nick=$1"
    user_id = await DB.get_pool().fetchrow(q, user.nick)
    user_id = user_id["user_id"]

    query = "INSERT INTO user_quiz_taken (quiz_id, user_id) VALUES ($1, $2)"
    await DB.get_pool().execute(query, id, user_id)

async def select_user_quiz_taken(user_nick, id):
    """Selects data is user has taken a quiz

    :param user_nick: Nick of user
    :type user_nick: str
    :param id: Id of quiz
    :type id: int
    :return: None if quiz has not been taken
    :rtype: None or Row
    """
    q = "SELECT user_id FROM users WHERE nick=$1"
    user_id = await DB.get_pool().fetchrow(q, user_nick)
    user_id = user_id["user_id"]

    query = "SELECT 1 FROM user_quiz_taken WHERE quiz_id=$1 AND user_id=$2"
    return await DB.get_pool().fetchrow(query, id, user_id)

async def select_user_from_db(id: int):
    """Selects user from db

    :param id: Id of user
    :type id: int
    :return: User model
    :rtype: User object
    """
    user = dict(await perform_select_sql(GetUser, id))

    return GetUser.from_dict(user)