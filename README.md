# python-lyrics-ppt-creator

Python app to create lyrics ppt files

# How to set up local workspace for development

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
python3 -m pip install -r requirements.txt
```

OR

```
python3 -m pip install pylint
python3 -m pip install Flask
python3 -m pip install python-pptx
python3 -m pip install Werkzeug
```

Below command runs the flask app

```
flask run
```

# Miscellaneous Commands

Create requirements.txt file

```
python3 -m pip freeze > requirements.txt
```

# Commands to run on pythonanywhere.com console

```
git clone https://github.com/dongkyu9315/python-lyrics-ppt-creator.git
```

```
mkvirtualenv env --python='/usr/bin/python3.9'
```

```
pip install -r requirements.txt
```

# References

python-pptx: https://python-pptx.readthedocs.io/en/latest/

Flask: https://flask.palletsprojects.com/en/2.3.x/
