FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_HOST=host.docker.internal
ENV DB_PORT=5432
ENV DB_NAME=crimedb
ENV DB_USER=postgres
ENV DB_PASSWORD=Ma314DBS@

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY App ./App

EXPOSE 8000

CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"]