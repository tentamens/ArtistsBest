FROM python:3.7-slim

WORKDIR /app

ADD . /app

RUN pip install fastapi libsql_client python-dotenv python_Levenshtein Requests starlette uvicorn

EXPOSE 6969

CMD ["python", "index.py"]