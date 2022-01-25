#!/bin/sh

export DEBUG=1

cd $(dirname $0)
# pip install -r requirements.txt
python server.py
