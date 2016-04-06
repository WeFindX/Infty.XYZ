env:
	virtualenv .env
	pip install -r requirements.txt
	npm install -g bower

prepare:
	.env/bin/python src/manage.py bower install --settings=conf.local
	.env/bin/python src/manage.py collectstatic --noinput --settings=conf.local

shell:
	.env/bin/python src/manage.py shell --settings=conf.local

runserver:
	.env/bin/python src/manage.py runserver --settings=conf.local

test:
	.env/bin/python src/manage.py test --settings=conf.test

wsgi:
	uwsgi\
		--http 127.0.0.1:8000\
		--need-app\
		--disable-logging\
		--wsgi-file src/wsgi.py\
		--processes 1\
		--threads 5\
		--py-autoreload 1\
		--home .env

clean:
	@echo "--> Cleaning pyc files"
		find . -name "*.pyc" -delete
