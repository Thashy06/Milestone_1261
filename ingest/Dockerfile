FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest.py .

COPY ds_salaries.csv .

CMD ["python", "ingest.py"]
