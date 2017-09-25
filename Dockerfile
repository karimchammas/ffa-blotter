# COPY FROM ffapb/ffa-jobs-settings:Dockerfile

# to test: > docker run -it --entrypoint /bin/sh python:alpine
FROM python:alpine
RUN apk --update add git gcc musl-dev g++ freetds-dev
RUN pip3 install pew

# -i arguments copied from requirements.txt
# Reason for not using the requirements.txt is that in Dockerfile
# after a COPY, layers are not cached
RUN pew new \
  --python=python3 \
  -d \
  -i Django==1.10.5 \
  -i django-bootstrap3==8.1.0 \
  -i django-pagination-bootstrap==1.2 \
  -i Django-Select2==5.8.10 \
  -i django-smtp-ntlm-backend==0.0.3 \
  -i numpy==1.12.0 \
  -i openpyxl==2.4.5 \
  -i pandas==0.18.1 \
  -i progressbar33==2.4 \
  -i xlrd==1.0.0 \
  -i git+https://github.com/pymssql/pymssql.git
  -i git+https://github.com/shadiakiki1986/python-ntlm3.git@feature_smtp
  -i django-tables2 \
  -i django-filter \
  -i django-reversion \
  -i jsondiff \
  -i mayan-api_client \
  FFA_BLOTTER

WORKDIR /var/lib/blotter
COPY . .
RUN test -f manage.sh && test -f importMarketflow.sh
RUN chmod +x /var/lib/blotter/docker-entry.sh

ENTRYPOINT /var/lib/blotter/docker-entry.sh
