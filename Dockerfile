FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV ENVIRONMENT dev

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY uwsgi.ini /app/

COPY ./Code /app