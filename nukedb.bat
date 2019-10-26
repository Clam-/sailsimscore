@echo off
set VENV=%CD%\env

del ..\sailsimscore.sqlite
rmdir /q /s sailsimscore\alembic\versions
mkdir sailsimscore\alembic\versions
%VENV%\Scripts\alembic -c ..\sailsimscore.ini revision --autogenerate -m "init"
%VENV%\Scripts\alembic -c ..\sailsimscore.ini upgrade head
%VENV%\Scripts\initialize_sailsimscore_db ..\sailsimscore.ini
