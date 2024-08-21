@echo off
REM Get the directory where the batch file is located
cd D:\TUGAS KULIAH\Project Tugas Akhir\TugasAkhir\

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application
py "app testing.py"