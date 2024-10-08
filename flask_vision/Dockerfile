# python version
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# copy the current directory contents into the container at /app
COPY . /app

# install the requirements
RUN pip install --no-cache-dir -r requirements.txt

# port
EXPOSE 5000

#
ENV NAME World

# Run app.py
CMD ["python", "app.py"]
