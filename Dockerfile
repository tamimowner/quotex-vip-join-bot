FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway will set PORT
ENV PORT=8000

# We will run both bot and postback via a simple entry script
CMD ["python", "run.py"]
