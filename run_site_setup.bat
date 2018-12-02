@echo off

cd %2\%1
rmdir /Q /S .\site_env
virtualenv -p python3 .\site_env
call .\site_env\Scripts\activate.bat
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
IF "%~3" == "" (
    powershell -Command "echo ""from django.contrib.auth.models import User; User.objects.create_superuser('%3', '%4', '%5')"" | Out-File Dockerfile"
)
