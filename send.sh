python3 mysite/manage.py collectstatic --noinput --clear
python3 mysite/manage.py makemigrations
python3 mysite/manage.py migrate
move mysite/mysite/settings.py mysite/mysite/localsettings.py
move mysite/mysite/herokusettings.py mysite/mysite/settings.py
git add .
git commit -m "auto"
git push --set-upstream origin main
git push heroku main:main --force
move mysite/mysite/settings.py mysite/mysite/herokusettings.py
move mysite/mysite/localsettings.py mysite/mysite/settings.py
heroku run python mysite/manage.py migrate
