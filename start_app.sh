#!/bin/bash

git pull
source .env/bin/activate
pip3 install -r requirements.txt
python3 app.py
