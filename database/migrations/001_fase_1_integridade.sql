--
-- PostgreSQL database dump
--

\restrict vfbin0fFLMreZ6TGZwu1aPqlLhHt5VU8WkSpj1C2fbA5OpVfkavIxQOafPcqY5R

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: status_emprestimo; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.status_emprestimo AS ENUM (
    'ATIVO',
    'DEVOLVIDO',
    'ATRASADO',
    'CANCELADO',
    'EMPRESTADO'
);


ALTER TYPE public.status_emprestimo OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alunos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alunos (
    id integer NOT NULL,
    nome character varying(100),
    matricula character varying(20)
);


ALTER TABLE public.alunos OWNER TO postgres;

--
-- Name: alunos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.alunos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.alunos_id_seq OWNER TO postgres;

--
-- Name: alunos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.alunos_id_seq OWNED BY public.alunos.id;


--
-- Name: emprestimos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.emprestimos (
    id integer NOT NULL,
    livro_id integer NOT NULL,
    aluno_id integer NOT NULL,
    data_emprestimo date NOT NULL,
    data_devolucao date,
    status public.status_emprestimo DEFAULT 'ATIVO'::public.status_emprestimo NOT NULL
);


ALTER TABLE public.emprestimos OWNER TO postgres;

--
-- Name: emprestimos_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.emprestimos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.emprestimos_id_seq OWNER TO postgres;

--
-- Name: emprestimos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.emprestimos_id_seq OWNED BY public.emprestimos.id;


--
-- Name: livros; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.livros (
    id integer NOT NULL,
    titulo character varying(100),
    autor character varying(100),
    ano_publicacao integer,
    quantidade integer
);


ALTER TABLE public.livros OWNER TO postgres;

--
-- Name: livros_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.livros_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.livros_id_seq OWNER TO postgres;

--
-- Name: livros_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.livros_id_seq OWNED BY public.livros.id;


--
-- Name: alunos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alunos ALTER COLUMN id SET DEFAULT nextval('public.alunos_id_seq'::regclass);


--
-- Name: emprestimos id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emprestimos ALTER COLUMN id SET DEFAULT nextval('public.emprestimos_id_seq'::regclass);


--
-- Name: livros id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.livros ALTER COLUMN id SET DEFAULT nextval('public.livros_id_seq'::regclass);


--
-- Data for Name: alunos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alunos (id, nome, matricula) FROM stdin;
1	João Silva	20260000000000000001
2	Maria Oliveira	20260000000000000002
3	Carlos Santos	20260000000000000003
4	Ana Souza	20260000000000000004
5	Pedro Costa	20260000000000000005
6	Juliana Alves	20260000000000000006
7	Lucas Pereira	20260000000000000007
8	Fernanda Lima	20260000000000000008
9	Rafael Martins	20260000000000000009
10	Camila Rocha	20260000000000000010
\.


--
-- Data for Name: emprestimos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.emprestimos (id, livro_id, aluno_id, data_emprestimo, data_devolucao, status) FROM stdin;
1	1	1	2026-07-01	2026-07-14	DEVOLVIDO
2	2	2	2026-07-05	2026-07-18	DEVOLVIDO
3	3	3	2026-07-10	\N	ATIVO
4	4	4	2026-07-12	2026-07-25	DEVOLVIDO
5	5	5	2026-07-15	\N	ATRASADO
6	6	6	2026-07-20	2026-08-02	DEVOLVIDO
7	7	7	2026-07-25	\N	ATIVO
8	8	8	2026-07-28	\N	ATIVO
9	9	9	2026-08-01	\N	ATIVO
10	10	10	2026-08-03	\N	CANCELADO
11	1	1	2026-08-09	2026-09-01	DEVOLVIDO
12	11	3	2026-08-08	2026-09-09	EMPRESTADO
\.


--
-- Data for Name: livros; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.livros (id, titulo, autor, ano_publicacao, quantidade) FROM stdin;
1	Dom Casmurro	Machado de Assis	1899	3
2	Memórias Póstumas de Brás Cubas	Machado de Assis	1881	2
3	O Cortiço	Aluísio Azevedo	1890	4
4	Capitães da Areia	Jorge Amado	1937	3
5	Vidas Secas	Graciliano Ramos	1938	2
6	Grande Sertão: Veredas	João Guimarães Rosa	1956	2
7	A Hora da Estrela	Clarice Lispector	1977	3
8	1984	George Orwell	1949	5
9	O Hobbit	J. R. R. Tolkien	1937	4
10	Harry Potter e a Pedra Filosofal	J. K. Rowling	1997	5
11	Jantar Secreto	Raphael Montes	2016	1
\.


--
-- Name: alunos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.alunos_id_seq', 10, true);


--
-- Name: emprestimos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.emprestimos_id_seq', 12, true);


--
-- Name: livros_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.livros_id_seq', 11, true);


--
-- Name: alunos alunos_matricula_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_matricula_key UNIQUE (matricula);


--
-- Name: alunos alunos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alunos
    ADD CONSTRAINT alunos_pkey PRIMARY KEY (id);


--
-- Name: emprestimos emprestimos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emprestimos
    ADD CONSTRAINT emprestimos_pkey PRIMARY KEY (id);


--
-- Name: livros livros_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.livros
    ADD CONSTRAINT livros_pkey PRIMARY KEY (id);


--
-- Name: emprestimos emprestimos_aluno_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emprestimos
    ADD CONSTRAINT emprestimos_aluno_id_fkey FOREIGN KEY (aluno_id) REFERENCES public.alunos(id);


--
-- Name: emprestimos emprestimos_livro_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.emprestimos
    ADD CONSTRAINT emprestimos_livro_id_fkey FOREIGN KEY (livro_id) REFERENCES public.livros(id);


--
-- PostgreSQL database dump complete
--

\unrestrict vfbin0fFLMreZ6TGZwu1aPqlLhHt5VU8WkSpj1C2fbA5OpVfkavIxQOafPcqY5R

