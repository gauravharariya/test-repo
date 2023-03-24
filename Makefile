PYTHON_VERSION=3.9.1
PYENV_VERSION=$(shell which pyenv)

setup :
	( \
		if [ -z $(PYENV_VERSION) ] ; then brew install pyenv ; else echo "pyenv already installed"; fi ; \
		brew install openssl readline sqlite3 xz zlib; \
		echo N | pyenv install $(PYTHON_VERSION) ; \
		pyenv local $(PYTHON_VERSION); \
		python -m venv venv; \
		source venv/bin/activate; \
		pip install --upgrade pip; \
		pip install -r requirements/local.txt; \
	)

clean:
	rm -rf venv


run:
	( \
		source venv/bin/activate; \
		python run.py; \
	)

format:
	black --config .black.cfg ./app

lint-check:
	black --check --config .black.cfg ./app
	prospector --profile-path .prospector.yml ./app

test:
	pytest --cov=app tests/ --cov-config=.coveragerc --cov-report html