# Basic take on a blog using Google App Engine

Blog created based on https://github.com/potatolondon/djappengine repo with minor changes to run tests with Django client and to use newer SDK (1.9.5)

You can check it out how it's running on GAE: http://blog-karol-duleba.appspot.com/

## Requirements

Google Appengine Python SDK 1.9.5 (for development)

## Usage

Thanks to the base reapo usage is very simple 

Assumptions:
- You have GAE SDK v1.9.5
- You are in repo

### Run locally

    ./serve.sh

Then you can visit:
- app: http://localhost:8080
- admin: http://localhost:8000

### To deploy

    appcfg.py update .

### To start local shell

    ./shell

### Running tests

    ./test.sh

