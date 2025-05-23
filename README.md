# CIC Minichallenge 1: Iseni - Zemp
This Repo was built for the minichallenge in the module CIC (Cloud infrastructure and computing)

The task was to built an app / dashboard using a cloud API. We used Flask as a REST-API and put it in to a docker image.

The Dashboard is able to find the name of a celebrity based on an uploaded image.

## How to use the Dashboard to detect celebrities

after cloning the repo with git clone <repository-url> run the following commands:

First you need to register yourself at [aws](https://aws.amazon.com/de/rekognition/) and create a free account. The Framework Celebrity Rekognition has a free use for small projects. After you get your credentials you need to create a `.env` file and save them into it which should look like:
```bash
AWS_ACCESS_KEY_ID=access-key
AWS_SECRET_ACCESS_KEY=secret-access-key
AWS_REGION=your-chosen-region
MONITOR_URL=http://monitor:5001
WORKER_ID=worker_1
```

create a virtual environment with conda or venv

with conda:
```bash
conda create --name <environment-name> python=3.9
conda activate <environment-name>
```

with venv: 
```bash
python3 -m venv venv
```

activate environment with mac or Liniux:
```bash
source venv/bin/activate
```

activate environment with Windows:
```bash
venv\Scripts\activate
```

inside the IDE terminal, run the following commands:
```bash
docker-compose up --build
```
and the app should be running on http://127.0.0.1:5002/

- You can then upload an image as png, jpg or jpeg file and press the button "upload"
- Et voila, here is your celebrity! :)


