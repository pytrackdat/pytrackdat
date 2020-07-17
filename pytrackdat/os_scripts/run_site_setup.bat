@echo off

cd "%3\%2"
rmdir /Q /S site_env > nul 2> nul
virtualenv -p python3 site_env > nul 2> nul
if errorlevel 1 (
    virtualenv -p python site_env
)
call site_env\Scripts\activate.bat
pip install -r requirements.txt
if "%~9" == "True" (
    pip install -r requirements_gis.txt
)
python manage.py makemigrations
python manage.py migrate
if "%~4" == "" (
    powershell -Command "echo ""from django.contrib.auth.models import User; User.objects.create_superuser('%4', '%5', '%6')"" | Out-File Dockerfile"
)
deactivate

rem Remove virtual environment if this is a production build
if "%~8" == "True" (
    rmdir /Q /S site_env > nul 2> nul
)
