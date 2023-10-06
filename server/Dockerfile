FROM python:3.9.16-alpine
WORKDIR /code

RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN apk add --no-cache libmagic
RUN apk add --no-cache poppler-utils

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=80"]