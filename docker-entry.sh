#!/bin/sh

# launch django server
# ATM using the dev built-in server .. will move later to nginx maybe
pew in FFA_BLOTTER python manage.py migrate

# Running createsuperuser should be done manually by the admin upon docker-compose up for example
# pew in FFA_ES_SPLITTER python manage.py createsuperuser --no-input --username admin

# launch syslog
syslogd

# copy cron
echo "12 */3  * * * /bin/sh /var/lib/blotter/importMarketflow.sh && curl -fsS --retry 3 $HCHK_IMPORT > /dev/null | logger -t import" >> /etc/crontabs/root
echo "0  9 25 * * /bin/sh /var/lib/blotter/manage.sh reminder  && curl -fsS --retry 3 $HCHK_REMINDER > /dev/null | logger -t reminder" >> /etc/crontabs/root


# run server
pew in FFA_BLOTTER  python manage.py runserver 0.0.0.0:8000 | logger -t "runserver" &

# wait 1 second for the cron above to send its start output to syslog
sleep 1 

# tail the logs
tail -f /var/log/messages
