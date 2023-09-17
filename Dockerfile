FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PYTHONPATH "${PYTHONPATH}:/code/django_emailing_server"
ENV PYTHONPATH "${PYTHONPATH}:/code/django_emailing_server/django_emailing_server"

# Install/Update Pip
RUN pip install --upgrade pip
RUN pip3 install pipenv

WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

COPY . /code/

WORKDIR /django_emailing_server

EXPOSE 8000

# Run with runserver
ENTRYPOINT [ "python", "-m", "server" ]
