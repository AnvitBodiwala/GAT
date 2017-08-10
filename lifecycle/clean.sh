#!/bin/bash 

echo "CLEAN:"
echo "REMOVING .pyc FILES"
find .. -name \*.pyc -delete

echo "REMOVING .bak FILES"
find .. -name \*.bak -delete

echo "REMOVING __pycache__ DIRS"
find .. -name __pycache__ -type d -delete

echo "REMOVING nltk downloads"
find ../nltk_downloads/ -type d -not -name 'track_me' -delete

echo "REMOVING static/temp"
find ../static/temp/ -type f -not -name 'pylog.txt' | xargs rm -f

echo "CLEAN SUCCESSFUL"
