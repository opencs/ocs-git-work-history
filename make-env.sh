#!/bin/bash

if ! [ -d .env ]; then
	python -m venv .env
fi
source .env/bin/activate
pip install -r requirements.txt

echo "**********************************************************"
echo "Run 'source .env/bin/activate' to activate the virtualenv."
echo "**********************************************************"


