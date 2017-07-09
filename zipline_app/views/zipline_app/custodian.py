# THIS FILE IS MOSTLY COPIED FROM account.py

from django.urls import  reverse_lazy
from django.views import generic
from ...models.zipline_app.custodian import Custodian

class CustodianCreate(generic.CreateView):
  model = Custodian
  exclude = []
  success_url = reverse_lazy('zipline_app:custodians-list')

class CustodianList(generic.ListView):
  model = Custodian

class CustodianDelete(generic.DeleteView):
  model = Custodian
  success_url = reverse_lazy('zipline_app:custodians-list')

class CustodianDetailView(generic.DetailView):
  model = Custodian

class CustodianUpdateView(generic.UpdateView):
  model = Custodian
  exclude = []
  success_url = reverse_lazy('zipline_app:custodians-list')
