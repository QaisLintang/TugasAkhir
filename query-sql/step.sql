SET @sql_text=
        CONCAT (
        "SELECT
         qa.id AS attempt_id,
		u.id AS user_id,
    u.firstname,
    u.lastname,
    c.fullname AS course_name,
    q.name AS quiz_name,
    qa.uniqueid,
    qa.timestart,
    qa.timefinish,
    qa.sumgrades AS score,
    qat.id AS question_attempt_id,
    qas.id AS step_id,
    qas.state AS step_state,  -- Include the state of each step
    qas.timecreated AS step_start_time,
    next_step.timecreated AS next_step_time,
    next_step.timecreated - qas.timecreated AS time_spent_on_question
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
JOIN
    mdl_question_attempts qat ON qa.uniqueid = qat.questionusageid
JOIN
    mdl_question_attempt_steps qas ON qat.id = qas.questionattemptid
LEFT JOIN
    mdl_question_attempt_steps next_step ON qas.questionattemptid = next_step.questionattemptid AND qas.sequencenumber = next_step.sequencenumber - 1
WHERE
    qa.state = 'finished'
    AND cm.id = 10
ORDER BY
    qa.timefinish DESC, qat.id, qas.timecreated
INTO OUTFILE '/var/lib/mysql-files/mysql-dump-"
        , DATE_FORMAT( NOW() ,'%Y-%m-%d_%H:%i:%s')
        , "_log_step.csv'
FIELDS TERMINATED BY ','
ENCLOSED BY '\"'
LINES TERMINATED BY '\n'
");

PREPARE s1 FROM @sql_text;
EXECUTE s1;
DROP PREPARE s1;
