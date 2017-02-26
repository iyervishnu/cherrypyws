#!/bin/bash

NAME=”cherryscraper”                                # Name of the application
APPDIR=/home/ubuntu/www/cherryscrapper              # Project directory

cd $APPDIR

source /home/ubuntu/.virtualenvs/cherryscrapper/bin/activate 

python server.py