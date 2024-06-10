# How to run
1. 
```bash
source be-flask/bin/activate
```
2.
```bash
python3 app.py
```

# Routes
```bash
/
```
to access main display

```bash
/get_data
```
to download data from sandbox to local computer

```bash
/api/daftar_peserta
```
to fetch json data of peserta in the current shift

```bash
/get_summary
```
to fetch json data of monthly summary

```bash
/api/get_cases
```
to fetch json data of archived cases from database (local)

# Database
Create local database for testing
```SQL
CREATE TABLE `moodle`.`case_history` (`cases` JSON NOT NULL ) ENGINE = InnoDB;
```
Add this after creating table to prevents duplicates
```SQL
ALTER TABLE `case_history` ADD UNIQUE(`cases`);
```