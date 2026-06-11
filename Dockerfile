FROM python:3.13-slim

# Keep system-level environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Removed hardcoded database credentials here! 
# They will be injected at runtime via the .env file.

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY App ./App

EXPOSE 8000

CMD ["uvicorn", "App.main:app", "--host", "0.0.0.0", "--port", "8000"]