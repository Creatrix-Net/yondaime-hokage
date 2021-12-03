#!/bin/bash
pip install --upgrade virtualenv
virtualenv env
env/scripts/activate
pip install --upgrade -r requirements.txt