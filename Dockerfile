FROM python:3.7-slim


# Create the directory if it doesn't exist
RUN mkdir -p /usr/files

# Set the directory as the working directory
WORKDIR /usr/files


RUN pip install fastapi libsql_client python-dotenv python_Levenshtein Requests starlette uvicorn beautifulsoup4 google-auth

EXPOSE 6969

COPY . .

CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "6969"]