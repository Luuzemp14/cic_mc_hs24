## How to use the Dashboard to detect celebrities

after cloning the repo with git clone <repository-url> run the following commands:

create a virtual environment with conda or venv

with conda: 
conda create --name <environment-name> python=3.9
conda activate <environment-name>

with venv: 
python3 -m venv venv

activate environment with mac or Liniux:
source venv/bin/activate

activate environment with Windows:
venv\Scripts\activate


inside the IDE terminal, run the following commands:

docker-compose up --build

and the app should be running on http://localhost:5002/
and the worker should be running on http://localhost:5001/

- You can then upload an image as png, jpg or jpeg file and press the button "upload"
- Et voila, here is your celebrity! :) 
