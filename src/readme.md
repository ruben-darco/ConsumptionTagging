# Consumption Tagging example

This repository holds a few simple things that help explain how tagging in consumption service might work.
The main component is a webservice that:
- Uses the `usagepost.json` jsonschema to validate the data being POSTed
- Extracts the data (including 'generic tags')
- Pushes it to influxdb

There are example messages in the `data` directory.


This is very much POC/Testing code. There's no aim to produce something production ready.

## TODO
It would be good to demonstrate how we would read data. You can do that now in influx with some specific queries, but examples *in code* would be nice.


## Install
This is a python virtual environment, so typically:
```
git clone <repo>
cd directory
python -m venv .
source bin/activate
pip install -r requirements.txt
```

