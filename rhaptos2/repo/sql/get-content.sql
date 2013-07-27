-- arguments: id:string;
SELECT row_to_json(combined_rows) FROM (
    SELECT id_ as id, "mediaType", title, language, authors, translators, editors,
           "copyrightHolders", body, subjects, keywords, summary, "dateCreatedUTC",
           "dateLastModifiedUTC", "googleTrackingID"
    FROM cnxmodule
    WHERE id_ = %(id)s
) combined_rows;
