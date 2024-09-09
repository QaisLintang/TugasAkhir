SET @sql_text =
   CONCAT (
       "SELECT
    sl.id,
    u.id,
    u.firstname,
    u.lastname,
    c.fullname AS course_name,
    sl.component,
    sl.action,
    sl.target,
    sl.ip,
    q.id AS quiz_id,
    q.name AS quiz_name,
    sl.timecreated
FROM
    mdl_logstore_standard_log sl
JOIN
    mdl_user u ON sl.userid = u.id
JOIN
    mdl_course c ON sl.courseid = c.id
LEFT JOIN
    mdl_quiz q ON sl.objecttable = 'quiz' AND sl.objectid = q.id
WHERE
    c.id = 4 AND
    sl.timecreated BETWEEN 1704115229 AND 1724851154
ORDER BY
    sl.id DESC
INTO OUTFILE
       '/var/lib/mysql-files/mysql-dump-"
       , DATE_FORMAT( NOW(), '%Y-%m-%d_%H:%i:%s')
       , "_log.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '\"'
LINES TERMINATED BY '\n'
");

PREPARE s1 FROM @sql_text;
EXECUTE s1;
DROP PREPARE s1;

