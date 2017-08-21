# THIS FILE IS MOSTLY COPIED FROM account.py

from django.urls import  reverse_lazy
from django.views import generic
from ...models.zipline_app.custodian import Custodian

class CustodianCreate(generic.CreateView):
  model = Custodian
  fields = ['custodian_symbol','custodian_name']
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
  fields = ['custodian_symbol','custodian_name']
  success_url = reverse_lazy('zipline_app:custodians-list')

# copied from https://github.com/minerva22/ffa-jobs-settings/blob/master/emailffa/views.py
from ...filters import CustodianFilter
from django.shortcuts import render
def custodian_search(request):
  custodian_list = Custodian.objects.all()
  custodian_filter = CustodianFilter(request.GET, queryset=custodian_list)
  return render(request, 'zipline_app/custodian_search.html', {'filter': custodian_filter})
