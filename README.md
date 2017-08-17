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
pew new --python=python3 -d -r requirements.txt FFA_BLOTTER
```

## Usage

To run the development server

- Copy `manage.sh.dist` to `manage.sh` and modify variables inside
- The variables are explained in-line in `manage.sh.dist`
- They're mostly the email server credentials
- `./manage.sh runserver 0.0.0.0:8000`


To import marketflow accounts assets

- copy `importMarketflow.sh.dist` to `importMarketflow.sh` and modify variables inside
  - the variables are the hostname, port number, username, password, and database name
- `./manage.sh help importMarketflow`
- `./importMarketflow.sh ...`


## Development / Testing

- Copy `manage.sh.dist` and `importMarketflow.sh.dist` as indicated in the `Usage` section
- Run the tests with `./manage.sh test zipline_app.tests`

If running tests manually, could benefit from
- http://stackoverflow.com/questions/24011428/django-core-exceptions-improperlyconfigured-requested-setting-caches-but-setti#27455703
- http://stackoverflow.com/questions/26276397/django-1-7-upgrade-error-appregistrynotready-apps-arent-loaded-yet#26278999

To access a deeper namespace, use
```bash
> ./manage.sh test zipline_app       # will not test anything because I dont use tests.py anymore
> ./manage.sh test zipline_app.tests # will test everything

> ./manage.sh test zipline_app.tests.zipline_app.test_asset # will test only asset
> ./manage.sh test zipline_app.tests.zipline_app.test_zipline_app
> ./manage.sh test ...
```
## Under the hood
- [django](https://www.djangoproject.com/)
- [django-bootstrap3](https://github.com/dyve/django-bootstrap3)
- django-tables2
- django-filters
- pymssql
- ...

### Django cheatsheet
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

Django management
```bash
python manage.py migrate
python manage.py test zipline_app.tests
python manage.py createsuperuser
```
Reference
* [creating an admin user](https://docs.djangoproject.com/en/1.10/intro/tutorial02/#creating-an-admin-user)



When a model is modified:
```bash
python manage.py makemigrations zipline_app
python manage.py migrate
```

To squash migrations: `> ./manage.sh squashmigrations zipline_app 0003 0005`

Shell example
```
>>> from zipline_app.models.zipline_app.asset import Asset
>>> Asset.objects.filter(asset_symbol='0.01 HKD').count()
1
```
