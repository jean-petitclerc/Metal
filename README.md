# Metal

## Requirements ##

- Flask
- Flask-Script
- Flask-Bootstrap
- Flask-WTF
- email-validator
- psycog2 (Needs: yum install libpq-devel python-devel)

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Config ##

```
class Config(object):
    DEBUG = True
    ADMIN_EMAILID='jean.petitclerc@groupepp.com'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///data/metal.db'
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://user:password@server:port/db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'app secret key'
    SESSION_COOKIE_NAME = 'Metal'
```

## Create the DB ##

```
python
from main import db
db.create_all()
```

## Execution ##

```
python main.py runserver -p port -h host
```
