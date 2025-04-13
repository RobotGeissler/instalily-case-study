install:
    npm install --prefix ./frontend
    conda env create -f ./environment.yml

front:
    npm start --prefix ./frontend

back:
    python3 -m backend.main

build: