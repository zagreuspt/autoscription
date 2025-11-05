FROM python:3.11
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY src .
CMD ["gunicorn", "--bind", "0.0.0.0:80", "application:create_app(config=None)"]