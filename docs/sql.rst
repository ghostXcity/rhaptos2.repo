dbtest=> CREATE TABLE cnxacl (
    id_ SERIAL ,
    module_id character varying,
    folder_id character varying,
    collection_id character varying,
    user_id character varying,
    role_type character varying
);


module

5f663dd5-3032-4545-b918-73115eb9d8ff

user
b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4


INSERT INTO cnxacl
(module_id, user_id, role_type) 
VALUES
('5f663dd5-3032-4545-b918-73115eb9d8ff',
'b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4',
'aclrw');

b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4


dbtest=> select id_, title from cnxmodule WHERE EXISTS (SELECT 1 FROM cnxacl 
dbtest(> WHERE user_id = 'b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4' AND 
dbtest(> module_id = cnxmodule.id_);
