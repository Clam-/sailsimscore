@echo off
set VENV=%CD%\env
echo %%VENV%%\Scripts\pip

echo %%VENV%%\Scripts\pserve development.ini --reload

echo %%VENV%%\Scripts\alembic -c development.ini revision --autogenerate -m "init"

echo %%VENV%%\Scripts\alembic -c development.ini upgrade head

echo %%VENV%%\Scripts\initialize_sailsimscore_db development.ini
