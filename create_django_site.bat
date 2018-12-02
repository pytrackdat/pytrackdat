@echo off

cd "%2"
rmdir /Q /S tmp_env > nul 2> nul
rmdir /Q /S "%1" > nul 2> nul
virtualenv -p python3 tmp_env > nul 2> nul
if errorlevel 1 (
    virtualenv -p python tmp_env
)
call tmp_env\Scripts\activate.bat
pip install -r ..\util_files\requirements_setup.txt
python .\tmp_env\Scripts\django-admin startproject %1
copy /B ..\util_files\requirements.txt %1\
copy /B ..\util_files\Dockerfile %1\
copy /B ..\util_files\docker-compose.yml %1\
copy /B ..\util_files\nginx.conf %1\
cd %1
powershell -Command "(gc Dockerfile) -replace 'SITE_NAME', '%1' | Out-File Dockerfile"
python ./manage.py startapp core
xcopy ..\..\app_includes\ %1\
copy /B ..\..\common.py\ %1\
deactivate
