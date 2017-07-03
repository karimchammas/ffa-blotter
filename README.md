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
To serve the web app
```bash
python manage.py runserver 0.0.0.0:8000
```

To import marketflow accounts/assets
```bash
python manage.py importMarketflow --debug
```

## Environment variables required
For importing from marketflow sql server

    export PYMSSQL_SERVER=...
    export PYMSSQL_PORT=...
    export PYMSSQL_USERNAME=...
    export PYMSSQL_PASSWORD=...
    export PYMSSQL_DB=...

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
* [zipline](https://github.com/quantopian/zipline/)
  * [zipline/finance/order](https://github.com/quantopian/zipline/blob/master/zipline/finance/order.py)
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

### Zipline
* `pip3 install zipline` currently takes a long time (more than 15 mins on aws ec2)
* [Order](https://github.com/quantopian/zipline/blob/master/zipline/finance/order.py)
* [Blotter](https://github.com/quantopian/zipline/blob/3350227f44dcf36b6fe3c509dcc35fe512965183/zipline/finance/blotter.py#L123)
  * Line 123 shows usage for `Order`
  * Checks [test_blotter.py](https://github.com/quantopian/zipline/blob/3350227f44dcf36b6fe3c509dcc35fe512965183/tests/test_blotter.py)
  * will require an `AssetFinder` class .. I'll probably need to override this with my own class linking assets from marketflow? (what abuot new assets?)
