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
to access main display
```bash
/
```
to download data from sandbox to local computer
```bash
/get_data
```
to fetch json data of peserta in the current shift
```bash
/api/daftar_peserta
```
to fetch json data of monthly summary
```bash
/get_summary
```
to fetch json data of archived cases from database (local)
```bash
/api/get_cases
```

# Database
Create local database for testing
```SQL
CREATE TABLE `log_analyzer_db`.`case_history` (`cases` JSON NOT NULL ) ENGINE = InnoDB;
```