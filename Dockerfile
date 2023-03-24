FROM python:3.9-slim-buster as base-python

ENV APP_USER rostra
ENV APP_HOME /home/$APP_USER

ENV PYTHONPATH $APP_HOME
ENV PYTHONUNBUFFERED 1
ENV PYTHONWARNINGS ignore::UserWarning
ENV PYTHONDONTWRITEBYTECODE 1

## Install System Deps
RUN apt-get update && apt-get -y install --no-install-recommends git gcc make python3-dev
RUN rm -rf /var/lib/apt/lists/*

# Create the user
RUN groupadd -r $APP_USER
RUN useradd -r -g $APP_USER -d $APP_HOME -s /sbin/nologin -c "Rostra Application User" -m $APP_USER

# Allows docker to cache installed dependencies between builds
FROM base-python as python-deps

WORKDIR $APP_HOME

# Install Python Deps
COPY ./requirements.txt .
COPY ./requirements ./requirements
RUN pip install --no-cache-dir --timeout=180 -r requirements.txt

USER $APP_USER

FROM python-deps

# Adds our application code to the image
COPY . .

ENTRYPOINT ["make", "-s", "-f", "deployment/Makefile"]
CMD ["run-server"]
