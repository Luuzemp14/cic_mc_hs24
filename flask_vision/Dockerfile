# python version
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy the current directory contents into the container at /app
COPY . .

# port
EXPOSE 5002

# Run app.py
CMD ["python", "app.py"]
