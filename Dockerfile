FROM python:3.7-slim

WORKDIR /app

ADD . /app

RUN pip install fastapi libsql_client python-dotenv python_Levenshtein Requests starlette uvicorn beautifulsoup4 google-auth

EXPOSE 6969

CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "6969"]