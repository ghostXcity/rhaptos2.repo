dbtest=> CREATE TABLE cnxacl (
    id SERIAL ,
    moduleid character varying,
    folderid character varying,
    collectionid character varying,
    userid character varying,
    roletype character varying
);


module

5f663dd5-3032-4545-b918-73115eb9d8ff

user
b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4


INSERT INTO cnxacl
(moduleid, userid, roletype) 
VALUES
('5f663dd5-3032-4545-b918-73115eb9d8ff',
'b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4',
'aclrw');

b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4


dbtest=> select id_, title from cnxmodule WHERE EXISTS (SELECT 1 FROM cnxacl 
dbtest(> WHERE userid = 'b49ed1d0-caf9-4d53-8363-ba4c2f23e0d4' and 
dbtest(> moduleid = cnxmodule.id_);
