FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Flask environment variables
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=development

# Start de app
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
