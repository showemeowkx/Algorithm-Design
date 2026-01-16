
FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY . .

RUN mkdir -p ./files

CMD ["python", "main.py"]