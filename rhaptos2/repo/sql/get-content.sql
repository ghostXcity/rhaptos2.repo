-- arguments: id:string;
SELECT row_to_json(combined_rows) FROM (SELECT id_ as id, "mediaType", title, language, authors, "copyrightHolders", body, subjects, keywords, summary, "dateCreatedUTC", "dateLastModifiedUTC" FROM cnxmodule WHERE id_ = %(id)s) combined_rows;
