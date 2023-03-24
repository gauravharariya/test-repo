.ONESHELL:

prepare:
	echo "Running application using **`whoami`** user"

	echo "Run database migrations"
	flask db upgrade
	echo "Successfully run database migrations."

run-server: prepare
	echo "Running application using **`whoami`** user"

	echo "Starting Server"
	gunicorn -c gunicorn_cfg.py wsgi:application

