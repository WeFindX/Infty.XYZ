prepare-env:
	virtualenv .env
	pip install -r requirements.txt

shell:
	.env/bin/python src/manage.py shell --settings=conf.local

runserver:
	.env/bin/python src/manage.py runserver --settings=conf.local

run-wsgi:
	uwsgi --http 127.0.0.1:8000 --need-app --disable-logging --wsgi-file src/wsgi.py --processes 1 --threads 5 --home .env

clean:
	@echo "--> Cleaning pyc files"
		find . -name "*.pyc" -delete
