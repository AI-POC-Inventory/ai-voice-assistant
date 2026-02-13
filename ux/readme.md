pip install django
django-admin startproject ai_voice_assistant_web
cd ai_voice_assistant_web
python manage.py startapp assistants

#run existing app
cd .\ux\ai_voice_assistant_web\
python manage.py runserver

pip install google-auth google-auth-oauthlib google-api-python-client
