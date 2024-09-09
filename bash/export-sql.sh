#!/bin/bash
min=$(date +%Y-%m-%d-%T)
fullpath=/var/lib/mysql-files/$min

mysql -u root -padmin@123 moodle < ../query-sql/log.sql
mysql -u root -padmin@123 moodle < ../query-sql/step.sql
mysql -u root -padmin@123 moodle < ../query-sql/attempt.sql

mkdir $fullpath
mv /var/lib/mysql-files/*.csv $fullpath 
echo $fullpath
sleep 5
sshpass -p admin@12345 rsync -a --remove-source-files -e 'ssh -p 224' /var/lib/mysql-files/$min linux@180.250.135.11:~/backup-sql