--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: cnxrole_type; Type: TYPE; Schema: public; Owner: rhaptos2repo
--

CREATE TYPE cnxrole_type AS ENUM (
    'aclrw',
    'aclro'
);


ALTER TYPE public.cnxrole_type OWNER TO rhaptos2repo;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cnxcollection; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE cnxcollection (
    id_ character varying NOT NULL,
    title character varying,
    language character varying,
    "subType" character varying,
    subjects character varying[],
    keywords character varying[],
    summary character varying,
    authors character varying[],
    maintainers character varying[],
    "copyrightHolders" character varying[],
    editors character varying[],
    translators character varying[],
    acl character varying[],
    body character varying,
    "dateCreatedUTC" timestamp without time zone,
    "dateLastModifiedUTC" timestamp without time zone,
    "mediaType" character varying,
    "googleTrackingID" character varying
);


ALTER TABLE public.cnxcollection OWNER TO rhaptos2repo;

--
-- Name: cnxfolder; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE cnxfolder (
    id_ character varying NOT NULL,
    title character varying,
    contents character varying[],
    "dateCreatedUTC" timestamp without time zone,
    "dateLastModifiedUTC" timestamp without time zone,
    "mediaType" character varying,
    acl character varying[]
);


ALTER TABLE public.cnxfolder OWNER TO rhaptos2repo;

--
-- Name: cnxmodule; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE cnxmodule (
    id_ character varying NOT NULL,
    title character varying,
    authors character varying[],
    maintainers character varying[],
    "copyrightHolders" character varying[],
    editors character varying[],
    translators character varying[],
    acl character varying[],
    body character varying,
    language character varying,
    "subType" character varying,
    subjects character varying[],
    keywords character varying[],
    summary character varying,
    "dateCreatedUTC" timestamp without time zone,
    "dateLastModifiedUTC" timestamp without time zone,
    "mediaType" character varying,
    "googleTrackingID" character varying
);


ALTER TABLE public.cnxmodule OWNER TO rhaptos2repo;

--
-- Name: session_cache; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE session_cache (
    sessionid character varying NOT NULL,
    userdict character varying NOT NULL,
    session_startutc timestamp with time zone,
    session_endutc timestamp with time zone
);


ALTER TABLE public.session_cache OWNER TO rhaptos2repo;

--
-- Name: userrole_collection; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE userrole_collection (
    collection_uuid character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type NOT NULL,
    "beginDateUTC" timestamp without time zone,
    "endDateUTC" timestamp without time zone
);


ALTER TABLE public.userrole_collection OWNER TO rhaptos2repo;

--
-- Name: userrole_folder; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE userrole_folder (
    folder_uuid character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type NOT NULL,
    "beginDateUTC" timestamp without time zone,
    "endDateUTC" timestamp without time zone
);


ALTER TABLE public.userrole_folder OWNER TO rhaptos2repo;

--
-- Name: userrole_module; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE userrole_module (
    module_uri character varying NOT NULL,
    user_id character varying NOT NULL,
    role_type cnxrole_type,
    "beginDateUTC" timestamp without time zone,
    "endDateUTC" timestamp without time zone
);


ALTER TABLE public.userrole_module OWNER TO rhaptos2repo;


--
-- Name: cnxacl; Type: TABLE; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

CREATE TABLE cnxacl (
    id_ serial PRIMARY KEY,
    module_id character varying,
    collection_id character varying,
    folder_id character varying,
    user_id character varying NOT NULL,
    role_type cnxrole_type NOT NULL
);


ALTER TABLE public.cnxacl OWNER TO rhaptos2repo;


--
-- Name: cnxcollection_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY cnxcollection
    ADD CONSTRAINT cnxcollection_pkey PRIMARY KEY (id_);


--
-- Name: cnxfolder_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY cnxfolder
    ADD CONSTRAINT cnxfolder_pkey PRIMARY KEY (id_);


--
-- Name: cnxmodule_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY cnxmodule
    ADD CONSTRAINT cnxmodule_pkey PRIMARY KEY (id_);


--
-- Name: session_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY session_cache
    ADD CONSTRAINT session_cache_pkey PRIMARY KEY (sessionid);


--
-- Name: userrole_collection_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY userrole_collection
    ADD CONSTRAINT userrole_collection_pkey PRIMARY KEY (collection_uuid, user_id, role_type);


--
-- Name: userrole_folder_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY userrole_folder
    ADD CONSTRAINT userrole_folder_pkey PRIMARY KEY (folder_uuid, user_id, role_type);


--
-- Name: userrole_module_pkey; Type: CONSTRAINT; Schema: public; Owner: rhaptos2repo; Tablespace: 
--

ALTER TABLE ONLY userrole_module
    ADD CONSTRAINT userrole_module_pkey PRIMARY KEY (module_uri, user_id);


--
-- Name: userrole_collection_collection_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: rhaptos2repo
--

ALTER TABLE ONLY userrole_collection
    ADD CONSTRAINT userrole_collection_collection_uuid_fkey FOREIGN KEY (collection_uuid) REFERENCES cnxcollection(id_);


--
-- Name: userrole_folder_folder_uuid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: rhaptos2repo
--

ALTER TABLE ONLY userrole_folder
    ADD CONSTRAINT userrole_folder_folder_uuid_fkey FOREIGN KEY (folder_uuid) REFERENCES cnxfolder(id_);


--
-- Name: userrole_module_module_uri_fkey; Type: FK CONSTRAINT; Schema: public; Owner: rhaptos2repo
--

ALTER TABLE ONLY userrole_module
    ADD CONSTRAINT userrole_module_module_uri_fkey FOREIGN KEY (module_uri) REFERENCES cnxmodule(id_);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

