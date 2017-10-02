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

- Copy `zipline_project/settings_production.py.dist` to `zipline_project/settings_production.py` and modify variables
- They're mostly the email server credentials
- `pew in FFA_BLOTTER ./manage.py runserver 0.0.0.0:8000`
  - all `manage.py` commands below are shown without the `pew in FFA_BLOTTER` prefix for brevity


To import marketflow accounts assets

- copy `importMarketflow.sh.dist` to `importMarketflow.sh` and modify variables inside
  - the variables are the hostname, port number, username, password, and database name
- `./manage.py help importMarketflow`
- `./importMarketflow.sh ...`

To initialize model versions with [django-reversion](https://django-reversion.readthedocs.io/en/stable/commands.html)
- `./manage.py createinitialrevisions zipline_app.Order --comment="Initial revision."`
  - will output something like "Created 29 revisions" (where 29 is the number of instances)
  - "Whenever you register a model with django-reversion, run createinitialrevisions." ([ref](https://django-reversion.readthedocs.io/en/stable/api.html))

To trim model versions
- `./manage.py deleterevisions zipline_app.Order --keep=3 --days=30`


## Development / Testing

- Copy `importMarketflow.sh.dist` as indicated in the `Usage` section
- Run the tests with `./manage.py test zipline_app.tests`

If running tests manually, could benefit from
- http://stackoverflow.com/questions/24011428/django-core-exceptions-improperlyconfigured-requested-setting-caches-but-setti#27455703
- http://stackoverflow.com/questions/26276397/django-1-7-upgrade-error-appregistrynotready-apps-arent-loaded-yet#26278999

To access a deeper namespace, use
```bash
> ./manage.py test zipline_app       # will not test anything because I dont use tests.py anymore
> ./manage.py test zipline_app.tests # will test everything

> ./manage.py test zipline_app.tests.zipline_app.test_asset # will test only asset
> ./manage.py test zipline_app.tests.zipline_app.test_zipline_app
> ./manage.py test ...
```
## Under the hood
- [django](https://www.djangoproject.com/)
- [django-bootstrap3](https://github.com/dyve/django-bootstrap3)
- django-tables2
- django-filters
- pymssql
- [django-reversion](https://django-reversion.readthedocs.io/)
- jsondiff
  - alternative: [json-delta](http://json-delta.readthedocs.io/en/latest/index.html)
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

To squash migrations: `> ./manage.py squashmigrations zipline_app 0003 0005`

Shell example
```
>>> from zipline_app.models.zipline_app.asset import Asset
>>> Asset.objects.filter(asset_symbol='0.01 HKD').count()
1
```

To "unplace" order 133 for example
```
>>> from zipline_app.models.zipline_app.placement import Placement
>>> Placement.objects.filter(order_id=133).delete()
```

## Enable file upload

Here are the steps to run a [mayan edms](https://hub.docker.com/r/mayanedms/mayanedms/) docker service

- install docker using the [instructions](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#uninstall-docker-ce)
- enable non-sudo usage of docker with [this](http://askubuntu.com/questions/477551/ddg#477554)
  - `sudo groupadd docker; sudo gpasswd -a $USER docker; docker run hello-world`
- run the mayan docker image

```
docker pull mayanedms/mayanedms:2.7.3
docker run -d --name mayan-edms --restart=always -p 8000:80 -v mayan_data:/var/lib/mayan mayanedms/mayanedms:2.7.3
docker ps # will show health status = starting
# wait a minute
docker ps # should show health status = healthy
# for debugging, run docker logs <container id> (get container id from "docker ps")
```
- if on aws ec2, make sure that the security group allows port "8000" as selected above
- test that "http://ip:8000" is up
- set the env variables `MAYAN_HOST`, `MAYAN_ADMIN_USER`, and `MAYAN_ADMIN_PASSWORD`

For further administration
- go to "http://ip:8000" and log in with the admin the first time
- edit the admin details from top right: "user / edit details" and add admin email
- create tag in mayan-edms: ffa-blotter

## Docker
A Dockerfile is delivered in this repository.
To build it manually: `> docker build -t ffapb/ffa-blotter .`
Otherwise, use the [docker-blotter](https://github.com/ffapb/docker-blotter) repository
which has this repository as a git submodule
