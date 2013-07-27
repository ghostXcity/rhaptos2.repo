-- arguments: id:string;
SELECT row_to_json(combined_rows) FROM (
  SELECT id_ as id, "mediaType", title, "dateCreatedUTC", "dateLastModifiedUTC", contents FROM cnxfolder f WHERE id_ = %(id)s

) combined_rows;
