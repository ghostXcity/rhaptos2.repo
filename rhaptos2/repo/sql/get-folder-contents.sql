-- arguments: contents: array of strings;
SELECT row_to_json(combined_rows) FROM (
  SELECT id_ as id, "mediaType", title, "dateCreatedUTC", "dateLastModifiedUTC" FROM cnxmodule WHERE id_ = ANY (%(contents)s)

) combined_rows;
