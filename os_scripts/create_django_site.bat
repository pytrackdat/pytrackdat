@echo off

rem Enter the temporary site construction directory
cd "%2"

rem Remove existing site data if it exists
rmdir /Q /S tmp_env > nul 2> nul
rmdir /Q /S "%1" > nul 2> nul

rem Create and activate the virtual environment used for setup
virtualenv -p python3 tmp_env > nul 2> nul
if errorlevel 1 (
    virtualenv -p python tmp_env
)
call tmp_env\Scripts\activate.bat

rem Install the dependencies required for setup
pip install -r ..\util_files\requirements_setup.txt

rem Start the Django site
python .\tmp_env\Scripts\django-admin startproject "%1"

rem Copy pre-built files to the site folder
copy /B ..\util_files\requirements.txt "%1\"
copy /B ..\util_files\Dockerfile "%1\"
copy /B ..\util_files\docker-compose.yml "%1\"
copy /B ..\util_files\nginx.conf "%1\"
copy /B ..\util_files\export_labels.R "%1\"
copy /B ..\util_files\install_dependencies.R "%1\"

rem Enter the Django site directory
cd "%1"
powershell -Command "(gc Dockerfile) -replace 'SITE_NAME', '%1' | Out-File Dockerfile"

rem Create the Django application for the models
python manage.py startapp core

rem Copy pre-built application scripts to the application
xcopy ..\..\app_includes core /s /e
copy /B ..\..\common.py core

rem Deactivate the temporary setup virtual environment
deactivate
