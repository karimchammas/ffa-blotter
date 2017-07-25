# ffa-blotter [![Build Status](https://travis-ci.org/shadiakiki1986/ffa-blotter.svg?branch=master)](https://travis-ci.org/shadiakiki1986/ffa-blotter)
Blotter web application using django used in [FFA Private Bank](https://www.ffaprivatebank.com)

For the older blotter that wrapped the zipline engine, check [django-zipline-2](https://www.github.com/shadiakiki1986/django-zipline-2)

## Features
- add/del account/asset/order/fill
- fills match orders exactly
- side-by-side view, consecutive view
- order/fill edit history

Also check
- [CHANGELOG](CHANGELOG.md)
- [TODO](TODO.md)
- github issues

## Installation
Prerequisites
```bash
sudo pip3 install pew
sudo apt-get install g++ freetds-dev
pew new --python=python3 FFA_BLOTTER
pip install -r requirements.txt # Django datetime zipline
```

Django management
```bash
python manage.py migrate
python manage.py test zipline_app.tests
python manage.py createsuperuser
```
Reference
* [creating an admin user](https://docs.djangoproject.com/en/1.10/intro/tutorial02/#creating-an-admin-user)

## Usage
To serve the web app: `python manage.py runserver 0.0.0.0:8000`

To import marketflow accounts/assets: `python manage.py help importMarketflow`, where the command will need the hostname, port number, username, password, and database name

## Environment variables required
For sending email through a SMTP server with NTLM authentication

    export DEFAULT_FROM_EMAIL=from@email.com
    export EMAIL_HOST=smtp.mail.server.com
    export EMAIL_PORT=123
    export EMAIL_HOST_USER=domain\\user
    export EMAIL_HOST_PASSWORD=oasswird
    export BASE_URL=http://blotter.com # just for email footer link

## Testing
```bash
pew workon FFA_BLOTTER
POLLS_LOG_LEVEL=DEBUG python manage.py test zipline_app.tests
```
where the `POLLS_LOG_LEVEL` env variable is the django log level desired
as documented [here](https://docs.djangoproject.com/en/1.10/topics/logging/#loggers)
(default in `settings.py` is INFO)

If running tests manually, could benefit from
* http://stackoverflow.com/questions/24011428/django-core-exceptions-improperlyconfigured-requested-setting-caches-but-setti#27455703
* http://stackoverflow.com/questions/26276397/django-1-7-upgrade-error-appregistrynotready-apps-arent-loaded-yet#26278999

To access deeper namespace, use
```bash
> python manage.py test zipline_app       # will not test anything because I dont use tests.py anymore
> python manage.py test zipline_app.tests # will test everything

> python manage.py test zipline_app.tests.zipline_app.test_asset # will test only asset
> python manage.py test zipline_app.tests.zipline_app.test_zipline_app
> python manage.py test ...
```
## Under the hood
* [django](https://www.djangoproject.com/)
* [django-bootstrap3](https://github.com/dyve/django-bootstrap3)

### Django
Following the [django tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/)
```bash
pew workon FFA_BLOTTER
mkdir ffa-blotter
cd ffa-blotter
git init
django-admin startproject project
mv project/* .
git add *
```

When a model is modified:
```bash
python manage.py makemigrations zipline_app
python manage.py migrate
```

To squash migrations: `> ./manage.sh squashmigrations zipline_app 0003 0005`

## django shell example
```
>>> from zipline_app.models.zipline_app.asset import Asset
>>> Asset.objects.filter(asset_symbol='0.01 HKD').count()
1
```
