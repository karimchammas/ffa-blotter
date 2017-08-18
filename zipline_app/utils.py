import hashlib
from django.urls import  reverse_lazy
from os import getenv

def md5_wrap(string):
  return hashlib.md5(string.encode('utf-8')).hexdigest()

def redirect_index_or_local(myself,local):
  source = myself.request.POST.get('source')
  if source is not None and source!='':
    return reverse_lazy('zipline_app:%s'%source)
  if type(local) is str:
    return reverse_lazy(local)
  return local

import datetime
from django.utils import timezone
from django.contrib.auth.models import User

def now_minute():
  ts=timezone.now()
  ts = chopSeconds(ts)
  return ts

def chopSeconds(ts:datetime):
  #ts -= datetime.timedelta(seconds=ts.second, microseconds=ts.microsecond)
  #return ts
  return ts.replace(second=0, microsecond=0)

def myTestLogin(client):
  password = 'glass onion'
  user = User.objects.create_user(username='john', email='jlennon@beatles.com', password=password)
  response = client.login(username=user.username, password=password, follow=True)
  if not response:
    raise Exception("Failed to log in")
  return user

def getenv_or_fail(envName: str):
  value = getenv(envName)
  if value is None:
    raise Exception("Environment variable undefined: '%s'" % envName)
  return value

# render template to email body
# https://godjango.com/19-using-templates-for-sending-emails/
from  django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from django.template import Context
from django.conf import settings
from django.contrib import messages

def email_ctx(ctx, template_txt, template_html, subject, logger):
  ctx['domain'] = settings.BASE_URL
  message_plain = render_to_string(template_txt, ctx)
  message_html = get_template(template_html).render(Context(ctx))
  recipients = User.objects.exclude(email='').values_list('email', flat=True)
  logger.debug("recipients: %s"%', '.join(recipients))
  if len(recipients)==0:
    logger.debug("No users with emails to receive")
    return
  
  envVars = ("EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD")
  for ev in envVars:
    if not getattr(settings, ev):
      logger.debug("Email not sent because of missing env var: %s" % (ev))
      return
  res = send_mail(
    subject = settings.EMAIL_SUBJECT_PREFIX + subject,
    message = message_plain,
    from_email = settings.DEFAULT_FROM_EMAIL,
    recipient_list = recipients,
    html_message = message_html
  )
  if res==0:
    logger.debug("Failed to send email")

#-----------------------
# use jsondiff on django-reversions
from reversion.models import Version
from jsondiff import diff
from .models.zipline_app.asset import Asset
from .models.zipline_app.account import Account
def get_revision_diffs(order):
  # https://django-reversion.readthedocs.io/en/stable/api.html#loading-revisions
  revisions = Version.objects.get_for_object(order)
  if len(revisions)<=1: return []
  diffs = []
  nextVer = None
  # note that revisions is an array sorted in reverse cronological order
  # i.e. newest edits first
  for version in revisions:
    if nextVer is None:
      nextVer = version
      continue

    # https://github.com/ZoomerAnalytics/jsondiff#quickstart
    newDiff_D = diff(nextVer.field_dict, version.field_dict, syntax='symmetric')
    newDiff_S = []
    for k1,v1 in newDiff_D.items():
      if k1=='insert':
        for k2,v2 in v1.items():
          newDiff_S.append("Added %s: %s"%(k2,v2))
      elif k1=='delete':
        for k2,v2 in v1.items():
          newDiff_S.append("Deleted %s: %s"%(k2,v2))
      else:
        if k1=='account_id':
          k1='account'
          v1=[Account.objects.get(id=x) for x in v1]
        elif k1=='asset_id':
          k1='security'
          v1=[Asset.objects.get(id=x) for x in v1]

        newDiff_S.append("Changed %s from '%s' to '%s'"%(k1, v1[1], v1[0]))

    diffs.append(
      { 'date_created': nextVer.revision.date_created,
        'diff': ', '.join(newDiff_S)
      }
     )

    nextVer = version

  return diffs

