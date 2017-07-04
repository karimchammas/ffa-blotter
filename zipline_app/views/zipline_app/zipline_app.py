#from django.shortcuts import render
# Create your views here.

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from ...models.zipline_app.zipline_app import Order, Fill

class IndexView(generic.base.TemplateView):
    template_name = 'zipline_app/index.html'
