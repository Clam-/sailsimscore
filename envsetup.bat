@echo off
set VENV=%CD%\env
echo %%VENV%%\Scripts\pip

echo %%VENV%%\Scripts\pserve ..\sailsimscore.ini --reload

echo %%VENV%%\Scripts\alembic -c ..\sailsimscore.ini revision --autogenerate -m "init"

echo %%VENV%%\Scripts\alembic -c ..\sailsimscore.ini upgrade head

echo %%VENV%%\Scripts\initialize_sailsimscore_db ..\sailsimscore.ini
