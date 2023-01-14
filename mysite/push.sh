python3 manage.py collectstatic --noinput --clear
sleep 1
python3 manage.py makemigrations
sleep 1
python3 manage.py migrate
sleep 1
mv mysite/settings.py mysite/localsettings.py
sleep 1
mv mysite/herokusettings.py mysite/settings.py
sleep 1
git add .
sleep 1
git commit -m "auto"
sleep 1
git push main
sleep 1
git push heroku +HEAD:main
sleep 1
mv mysite/settings.py mysite/herokusettings.py
sleep 1
mv mysite/localsettings.py mysite/settings.py
sleep 1
heroku run python mysite/manage.py makemigrations
sleep 1
heroku run python mysite/manage.py migrate
