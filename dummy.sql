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
-- Name: dummy_tbl id; Type: DEFAULT; Schema: public; Owner: api
--

ALTER TABLE ONLY public.dummy_tbl ALTER COLUMN id SET DEFAULT nextval('public.dummy_tbl_id_seq'::regclass);


--
-- Data for Name: dummy_tbl; Type: TABLE DATA; Schema: public; Owner: api
--

COPY public.dummy_tbl (id, name) FROM stdin;
1	dummy
\.


--
-- Name: dummy_tbl_id_seq; Type: SEQUENCE SET; Schema: public; Owner: api
--

SELECT pg_catalog.setval('public.dummy_tbl_id_seq', 1, true);


--
-- PostgreSQL database dump complete
--

