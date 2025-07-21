FROM python:3.11-slim

WORKDIR /app

COPY requirements_prod.txt .

RUN pip install --no-cache-dir -r requirements_prod.txt

COPY . .

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD  ["streamlit", "run", "scripts/tourism_advisor_app.py", "--server.port=8080", "--server.address=0.0.0.0"]