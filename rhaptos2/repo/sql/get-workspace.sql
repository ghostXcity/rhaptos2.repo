-- arguments: user_id:string;
SELECT row_to_json(combined_rows) FROM (
  SELECT id_ as id, "mediaType", title, "dateCreatedUTC", "dateLastModifiedUTC"
  FROM cnxmodule
  WHERE id_ IN (
    SELECT module_uri FROM userrole_module WHERE user_id = %(user_id)s
  )

  UNION ALL

  SELECT id_ as id, "mediaType", title, "dateCreatedUTC", "dateLastModifiedUTC"
  FROM cnxfolder
  WHERE id_ IN (
    SELECT folder_uuid FROM userrole_folder WHERE user_id = %(user_id)s
  )

) combined_rows;
