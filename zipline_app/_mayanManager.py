from mayan_api_client import API
from django.contrib.auth.models import User
import os
# fileresponse from django.views.static import serve
from django.http import FileResponse

# https://gitlab.com/mayan-edms/python_api_client
class MayanManager:
  api = None
  def __init__(self, host, username, password):
    if host is None or username is None or password is None:
      return

    self.api = API(
      host=host,
      username=username,
      password=password
    )

  """
  Create a tag if not already there
  """
  def create_tag_if_not(self, tag_label:str):
    tags = self.api.tags.tags.get()
    sub = [x for x in tags['results'] if x['label']==tag_label]

    if len(sub)>1:
      raise Exception("More than one tag with label=%s"%(tag_label))

    if len(sub)==0:
      response = self.api.tags.tags.post({'label': tag_label, 'color': '#777777'})
      return response

    sub = sub[0]
    keys = ['label', 'color', 'id']
    result = {k: sub[k] for k in keys}
    return result

  """
  Convert order ID to string tag
  """
  def order_id_to_tag(self, order_id:int):
    return 'order '+str(order_id)

  """
  Upload documents with a specific tag
  """
  def upload_doc(self, f, tag_obj:dict):
    response = self.api.documents.documents.post({'document_type': 1}, files={'file': f})
    return response

  def delete_doc(self, doc_id:int):
    response = self.api.documents.documents(doc_id).delete()
    return response

  def attach_docs_to_tag(self, tag_obj:dict, doc_ids:list):
    # append the new doc to the tag docs
    # https://gitlab.com/mayan-edms/python_api_client/issues/3
    tag_id = tag_obj['id']
    current = [x['id'] for x in self.api.tags.tags(tag_id).documents.get()['results']]
    current = current + doc_ids
    current = list(set(current)) # make unique
    self.api.tags.tags(tag_id).put({
      'documents_pk_list': ','.join([str(x) for x in current]),
      'color':tag_obj['color'],
      'label':tag_obj['label']
    })


  """
  List docs with a specific tag
  """
  def docs_by_tag(self, tag:str):
    tags = {'count': 99999}
    sub = []
    count = 0
    page = 0
    while tags['count'] > count:
      page += 1
      tags = self.api.tags.tags.get(page=page)
      sub += [x for x in tags['results'] if x['label']==tag]
      count += len(tags['results'])

    if len(sub)==0: return []
    if len(sub)>1: raise Exception("More than one tag found")

    sub = sub[0]
    docs = self.api.tags.tags(sub['id']).documents.get()
    keys = ['label', 'url', 'id']
    result = [{k: x[k] for k in keys} for x in docs['results']]
    return result

  """
  Syncronize users between blotter and mayan edms
  """
  def create_user_if_not(self, blotter_user):
    mayan_users_obj = api.user_management.users.get()
    mayan_users_usernames = [x['username'] for x in mayan_users_obj]
    if blotter_user.username in mayan_users_usernames:
      return

    #blotter_users_obj = User.objects.all()
    #blotter_users_usernames = [x['username'] for x in blotter_users_obj]

    #to_add = set(blotter_users_usernames) - set(mayan_users_usernames)
    #for username in to_add:
      # user = User.objects.filter(username=username)
    self.api.user_management.users.post({
      'email':blotter_user.email,
      'password':'12345678', # ATM just use this
      'username':blotter_user.username,
      'first_name':'',
      'groups_pk_list':'',
      'last_name':''
    })

  # copied from zipline_app.download_builder#DownloadBuilder.fn2response
  # and from https://gitlab.com/mayan-edms/python_api_client
  # section "Downloading a document:"
  def download_doc(self, document_id):
    root = os.path.join('/', 'tmp', 'blotter')
    if not os.path.exists(root):
      os.mkdir(root)

    document = self.api.documents.documents(document_id).get()
    target = os.path.join(root, document['label'])
    with open(target, 'wb') as file_object:
      file_object.write(self.api.documents.documents(document_id).download.get())

    # print(document)
    response = FileResponse(
      open(target, 'rb'),
      content_type=document['latest_version']['mimetype']
    )
    response['Content-Disposition'] = 'attachment; filename="%s"'%document['label']
    return response
