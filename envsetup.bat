@echo off
set VENV=%CD%\env
echo %%VENV%%\Scripts\pip

echo %%VENV%%\Scripts\initialize_db development.ini

echo %%VENV%%\Scripts\pserve development.ini --reload
