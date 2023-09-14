FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install/Update Pip
RUN pip install --upgrade pip
RUN pip3 install pipenv

# Execute these commands as root
RUN mkdir /code

WORKDIR /code

# Install dependencies
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy

COPY . /code/

EXPOSE 8000

# Run with runserver
ENTRYPOINT [ "python", "-m", "server" ]
