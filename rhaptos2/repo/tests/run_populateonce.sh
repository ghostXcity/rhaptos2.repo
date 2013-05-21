python cleardb.py
nosetests --tc-file=../../../testing.ini wsgitests.py:test_post_module
nosetests --tc-file=../../../testing.ini wsgitests.py:test_post_collection
nosetests --tc-file=../../../testing.ini wsgitests.py:test_post_folder

CREATE TABLE session_cache(
   sessionid  character varying NOT NULL,
   userdict   character varying NOT NULL,
   session_startUTC timestamptz,
   session_endUTC timestamptz
);

ALTER TABLE ONLY session_cache
    ADD CONSTRAINT session_cache_pkey PRIMARY KEY (sessionid);


