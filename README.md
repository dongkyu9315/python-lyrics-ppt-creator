# python-lyrics-ppt-creator
Python app to create lyrics ppt files

# commands

Create a virtualenv with python3.9

```
python3.9 -m venv .env3.9
```

Activate the virtualenv

```
source .env3.9/bin/activate
```

Install dependencies

```
python3 -m pip install pylint
python3 -m pip install Flask
python3 -m pip install python-pptx
python3 -m pip install Werkzeug
```

Creating requirements.txt file

```
python3 -m pip freeze > requirements.txt
```

Below command runs the flask app

```
flask run
```