FROM python:3.10-slim

ENV PYTHONUNBUFFERED True

WORKDIR .
COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

RUN ls -la input/course
RUN pwd

CMD exec gunicorn --bind :5000 --workers 1 --threads 8 --timeout 0 app:app