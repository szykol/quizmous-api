--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2 (Debian 12.2-2.pgdg100+1)
-- Dumped by pg_dump version 12.2 (Debian 12.2-2.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: q_type; Type: TYPE; Schema: public; Owner: api
--

CREATE TYPE public.q_type AS ENUM (
    'YES_NO',
    'RADIO',
    'CHOICE',
    'OPEN'
);


ALTER TYPE public.q_type OWNER TO api;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dummy_tbl; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.dummy_tbl (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.dummy_tbl OWNER TO api;

--
-- Name: dummy_tbl_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.dummy_tbl_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dummy_tbl_id_seq OWNER TO api;

--
-- Name: dummy_tbl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.dummy_tbl_id_seq OWNED BY public.dummy_tbl.id;


--
-- Name: quiz; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.quiz (
    quiz_id integer NOT NULL,
    author integer,
    name character varying NOT NULL,
    description character varying NOT NULL
);


ALTER TABLE public.quiz OWNER TO api;

--
-- Name: quiz_answer; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.quiz_answer (
    answer_id integer NOT NULL,
    question_id integer NOT NULL,
    answer character varying NOT NULL
);


ALTER TABLE public.quiz_answer OWNER TO api;

--
-- Name: quiz_answer_answer_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.quiz_answer_answer_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_answer_answer_seq OWNER TO api;

--
-- Name: quiz_answer_answer_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.quiz_answer_answer_seq OWNED BY public.quiz_answer.answer_id;


--
-- Name: quiz_key; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.quiz_key (
    key_id integer NOT NULL,
    key character varying NOT NULL,
    quiz_id integer NOT NULL
);


ALTER TABLE public.quiz_key OWNER TO api;

--
-- Name: quiz_key_key_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.quiz_key_key_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_key_key_id_seq OWNER TO api;

--
-- Name: quiz_key_key_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.quiz_key_key_id_seq OWNED BY public.quiz_key.key_id;


--
-- Name: quiz_question; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.quiz_question (
    question_id integer NOT NULL,
    quiz_id integer NOT NULL,
    question character varying NOT NULL,
    type public.q_type NOT NULL,
    required boolean DEFAULT true NOT NULL
);


ALTER TABLE public.quiz_question OWNER TO api;

--
-- Name: quiz_question_question_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.quiz_question_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_question_question_id_seq OWNER TO api;

--
-- Name: quiz_question_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.quiz_question_question_id_seq OWNED BY public.quiz_question.question_id;


--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.quiz_quiz_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_quiz_id_seq OWNER TO api;

--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.quiz_quiz_id_seq OWNED BY public.quiz.quiz_id;


--
-- Name: quiz_user_answers; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.quiz_user_answers (
    user_answer_id integer NOT NULL,
    question_id integer,
    answer_id integer,
    value character varying,
    key_id integer NOT NULL
);


ALTER TABLE public.quiz_user_answers OWNER TO api;

--
-- Name: quiz_user_answers_user_answer_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.quiz_user_answers_user_answer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quiz_user_answers_user_answer_id_seq OWNER TO api;

--
-- Name: quiz_user_answers_user_answer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.quiz_user_answers_user_answer_id_seq OWNED BY public.quiz_user_answers.user_answer_id;


--
-- Name: user_quiz_taken; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.user_quiz_taken (
    id integer NOT NULL,
    user_id integer,
    quiz_id integer
);


ALTER TABLE public.user_quiz_taken OWNER TO api;

--
-- Name: user_quiz_taken_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.user_quiz_taken_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_quiz_taken_id_seq OWNER TO api;

--
-- Name: user_quiz_taken_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.user_quiz_taken_id_seq OWNED BY public.user_quiz_taken.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: api
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    nick character varying NOT NULL,
    password character varying NOT NULL,
    is_admin boolean DEFAULT false NOT NULL
);


ALTER TABLE public.users OWNER TO api;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: api
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO api;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: api
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: dummy_tbl id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.dummy_tbl ALTER COLUMN id SET DEFAULT nextval('public.dummy_tbl_id_seq'::regclass);


--
-- Name: quiz quiz_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz ALTER COLUMN quiz_id SET DEFAULT nextval('public.quiz_quiz_id_seq'::regclass);


--
-- Name: quiz_answer answer_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_answer ALTER COLUMN answer_id SET DEFAULT nextval('public.quiz_answer_answer_seq'::regclass);


--
-- Name: quiz_key key_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_key ALTER COLUMN key_id SET DEFAULT nextval('public.quiz_key_key_id_seq'::regclass);


--
-- Name: quiz_question question_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_question ALTER COLUMN question_id SET DEFAULT nextval('public.quiz_question_question_id_seq'::regclass);


--
-- Name: quiz_user_answers user_answer_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_user_answers ALTER COLUMN user_answer_id SET DEFAULT nextval('public.quiz_user_answers_user_answer_id_seq'::regclass);


--
-- Name: user_quiz_taken id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.user_quiz_taken ALTER COLUMN id SET DEFAULT nextval('public.user_quiz_taken_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: dummy_tbl; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.dummy_tbl (id, name) FROM stdin;
1	dummy
\.


--
-- Data for Name: quiz; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.quiz (quiz_id, author, name, description) FROM stdin;
1	1	Dummy Quiz	This is a dummy quiz for testing purposes
\.


--
-- Data for Name: quiz_answer; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.quiz_answer (answer_id, question_id, answer) FROM stdin;
1	2	Pizza
2	2	Burger
3	2	Sushi
4	3	Linkin Park
5	3	The Beatles
6	3	Metallica
7	3	Dire Straits
8	3	Pink Floyd
9	5	Black
10	5	Red
11	5	Blue
12	5	Yellow
13	6	Spring
14	6	Summer
15	6	Autumn
16	6	Winter
\.


--
-- Data for Name: quiz_question; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.quiz_question (question_id, quiz_id, question, type, required) FROM stdin;
1	1	Do you like quizes?	YES_NO	t
2	1	What is your favorite food?	RADIO	t
3	1	Select a band(s) you like	CHOICE	t
4	1	Describe your best holidays	OPEN	t
5	1	What is your favorite color?	RADIO	t
6	1	Which season do you like?	CHOICE	t
7	1	Tell us how to improve	OPEN	f
\.


--
-- Data for Name: quiz_user_answers; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.quiz_user_answers (user_answer_id, question_id, answer_id, value, key_id) FROM stdin;
\.


--
-- Data for Name: user_quiz_taken; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.user_quiz_taken (id, user_id, quiz_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.users (user_id, nick, password, is_admin) FROM stdin;
1	admin	ultr4SECRET	f
\.


--
-- Name: dummy_tbl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.dummy_tbl_id_seq', 5, true);


--
-- Name: quiz_answer_answer_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.quiz_answer_answer_seq', 16, true);


--
-- Name: quiz_question_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.quiz_question_question_id_seq', 8, true);


--
-- Name: quiz_quiz_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.quiz_quiz_id_seq', 2, true);


--
-- Name: quiz_user_answers_user_answer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.quiz_user_answers_user_answer_id_seq', 1, false);


--
-- Name: user_quiz_taken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.user_quiz_taken_id_seq', 1, false);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.users_user_id_seq', 1, true);


--
-- Name: quiz_answer quiz_answer_answer_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_answer
    ADD CONSTRAINT quiz_answer_answer_key UNIQUE (answer_id);


--
-- Name: quiz_answer quiz_answer_answer_question_id_unique; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_answer
    ADD CONSTRAINT quiz_answer_answer_question_id_unique UNIQUE (question_id, answer);


--
-- Name: quiz_answer quiz_answer_question_id_answer_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_answer
    ADD CONSTRAINT quiz_answer_question_id_answer_key UNIQUE (question_id, answer);


--
-- Name: quiz quiz_name_unique; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_name_unique UNIQUE (name);


--
-- Name: quiz_question quiz_question_question_id_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_question
    ADD CONSTRAINT quiz_question_question_id_key UNIQUE (question_id);


--
-- Name: quiz_question quiz_question_question_quiz_id_unique; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_question
    ADD CONSTRAINT quiz_question_question_quiz_id_unique UNIQUE (quiz_id, question);


--
-- Name: quiz_question quiz_question_quiz_id_question_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_question
    ADD CONSTRAINT quiz_question_quiz_id_question_key UNIQUE (quiz_id, question);


--
-- Name: quiz quiz_quiz_id_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_quiz_id_key UNIQUE (quiz_id);


--
-- Name: quiz_key uniquekey; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_key
    ADD CONSTRAINT uniquekey UNIQUE (key);


--
-- Name: users users_nick_unique; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_nick_unique UNIQUE (nick);


--
-- Name: users users_user_id_key; Type: CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_id_key UNIQUE (user_id);


--
-- Name: quiz_answer quiz_answer_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_answer
    ADD CONSTRAINT quiz_answer_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quiz_question(question_id) ON DELETE CASCADE;


--
-- Name: quiz quiz_author_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz
    ADD CONSTRAINT quiz_author_fkey FOREIGN KEY (author) REFERENCES public.users(user_id);


--
-- Name: quiz_key quiz_key_quiz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_key
    ADD CONSTRAINT quiz_key_quiz_id_fkey FOREIGN KEY (quiz_id) REFERENCES public.quiz(quiz_id);


--
-- Name: quiz_question quiz_question_quiz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_question
    ADD CONSTRAINT quiz_question_quiz_id_fkey FOREIGN KEY (quiz_id) REFERENCES public.quiz(quiz_id) ON DELETE CASCADE;


--
-- Name: quiz_user_answers quiz_user_answers_answer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_user_answers
    ADD CONSTRAINT quiz_user_answers_answer_id_fkey FOREIGN KEY (answer_id) REFERENCES public.quiz_answer(answer_id);


--
-- Name: quiz_user_answers quiz_user_answers_key_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_user_answers
    ADD CONSTRAINT quiz_user_answers_key_id_fkey FOREIGN KEY (key_id) REFERENCES public.quiz_key(key_id);


--
-- Name: quiz_user_answers quiz_user_answers_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.quiz_user_answers
    ADD CONSTRAINT quiz_user_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.quiz_question(question_id);


--
-- Name: user_quiz_taken user_quiz_taken_quiz_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.user_quiz_taken
    ADD CONSTRAINT user_quiz_taken_quiz_id_fkey FOREIGN KEY (quiz_id) REFERENCES public.quiz(quiz_id);


--
-- Name: user_quiz_taken user_quiz_taken_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.user_quiz_taken
    ADD CONSTRAINT user_quiz_taken_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

