FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

HEALTHCHECK CMD python -c "import httpx; httpx.get('http://localhost:10000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
