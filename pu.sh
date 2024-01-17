python mysite/manage.py collectstatic --noinput
sleep 1 
python mysite/manage.py makemigrations
sleep 1 
python mysite/manage.py migrate
sleep 1 
mv mysite/mysite/settings.py mysite/mysite/localsettings.py
sleep 1 
mv mysite/mysite/herokusettings.py mysite/mysite/settings.py
sleep 1 
git add .
sleep 1 
git commit -m "auto"
sleep 1 
git push --set-upstream origin main
sleep 1 
heroku login
git push heroku main:main -f
sleep 1 
mv mysite/mysite/settings.py mysite/mysite/herokusettings.py
sleep 1 
mv mysite/mysite/localsettings.py mysite/mysite/settings.py
sleep 1 
heroku run python mysite/manage.py migrate
sleep 1 
