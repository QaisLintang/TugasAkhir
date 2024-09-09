SET @sql_text=
    CONCAT ( 
    "SELECT
    qa.id AS attempt_id,
    u.id,
    u.firstname,
    u.lastname,
    c.fullname AS course_name,
    q.name AS quiz_name,
                qa.uniqueid,
                qa.layout,
    qa.timestart,
    qa.timefinish,
    qa.sumgrades AS score
FROM
    mdl_quiz_attempts qa
JOIN
   mdl_user u ON qa.userid = u.id
JOIN
    mdl_quiz q ON qa.quiz = q.id
JOIN
    mdl_course c ON q.course = c.id
JOIN
    mdl_course_modules cm ON q.id = cm.instance AND cm.module = (SELECT id FROM mdl_modules WHERE name = 'quiz')       
WHERE
    qa.state = 'finished'
AND cm.id = 9
OR cm.id = 10
OR cm.id = 11
ORDER BY
    qa.timefinish DESC 
INTO OUTFILE
       './var/lib/mysql-files/mysql-dump-"
       , DATE_FORMAT( NOW() ,'%Y-%m-%d_%H:%i:%s')
       , "_log_attempt.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '\"'
LINES TERMINATED BY '\n'
");

PREPARE s1 FROM @sql_text;
EXECUTE s1;
DROP PREPARE s1;
