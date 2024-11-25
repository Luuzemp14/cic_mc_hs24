FROM python:3.8-slim

WORKDIR /monitor

COPY . .

RUN pip install --no-cache-dir flask

EXPOSE 5001

CMD ["python", "monitor.py"]