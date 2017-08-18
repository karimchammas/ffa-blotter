from django.conf.urls import url

from .views.zipline_app import zipline_app as views
from .views.zipline_app import order, asset, fill, account, autocomplete, custodian, placement

from django.views.generic import RedirectView
from django.urls import  reverse_lazy

app_name='zipline_app'
urlpatterns = [
    # ex: /<root>/
    url(r'^$', views.IndexView.as_view(), name='index'),

    # EDIT 2017-08-16: redirect all traffic to "/blotter/.../" to orders-list
    url(r'^blotter/sideBySide/$', RedirectView.as_view(url=reverse_lazy('zipline_app:orders-list')), name='blotter-sideBySide'),
    url(r'^blotter/concealed/$', RedirectView.as_view(url=reverse_lazy('zipline_app:orders-list')), name='blotter-concealed'),

    # ex: /<root>/accounts/
    url(r'^accounts/$', account.AccountList.as_view(), name='accounts-list'),
    # ex: /<root>/accounts/new/
    url(r'^accounts/new/$', account.AccountCreate.as_view(), name='accounts-new'),
    # ex: /<root>/accounts/5/
    url(r'^accounts/(?P<pk>[0-9]+)/$', account.AccountDetailView.as_view(), name='accounts-detail'),
    # ex: /<root>/accounts/1/update/
    url(r'^accounts/(?P<pk>[0-9]+)/update/$', account.AccountUpdateView.as_view(), name='accounts-update'),
    # ex: /<root>/accounts/1/delete/
    url(r'^accounts/(?P<pk>[0-9]+)/delete/$', account.AccountDelete.as_view(), name='accounts-delete'),

    # ex: /<root>/custodians/
    url(r'^custodians/$', custodian.CustodianList.as_view(), name='custodians-list'),
    # ex: /<root>/custodians/new/
    url(r'^custodians/new/$', custodian.CustodianCreate.as_view(), name='custodians-new'),
    # ex: /<root>/custodians/5/
    url(r'^custodians/(?P<pk>[0-9]+)/$', custodian.CustodianDetailView.as_view(), name='custodians-detail'),
    # ex: /<root>/custodians/1/update/
    url(r'^custodians/(?P<pk>[0-9]+)/update/$', custodian.CustodianUpdateView.as_view(), name='custodians-update'),
    # ex: /<root>/custodians/1/delete/
    url(r'^custodians/(?P<pk>[0-9]+)/delete/$', custodian.CustodianDelete.as_view(), name='custodians-delete'),

    # ex: /<root>/assets/
    url(r'^assets/$', asset.AssetList.as_view(), name='assets-list'),
    # ex: /<root>/assets/new/
    url(r'^assets/new/$', asset.AssetCreate.as_view(), name='assets-new'),
    # ex: /<root>/assets/5/
    url(r'^assets/(?P<pk>[0-9]+)/$', asset.AssetDetailView.as_view(), name='assets-detail'),
    # ex: /<root>/assets/1/delete/
    url(r'^assets/(?P<pk>[0-9]+)/delete/$', asset.AssetDelete.as_view(), name='assets-delete'),
    # ex: /<root>/assets/1/update/
    url(r'^assets/(?P<pk>[0-9]+)/update/$', asset.AssetUpdateView.as_view(), name='assets-update'),

    # ex: /<root>/fills/
    url(r'^fills/$', fill.FillList.as_view(), name='fills-list'),
    # ex: /<root>/fills/5/
    url(r'^fills/(?P<pk>[0-9]+)/$', fill.FillDetailView.as_view(), name='fills-detail'),
    # ex: /<root>/fills/new/
    url(r'^fills/new/(?P<order>[0-9]+)$', fill.FillCreate.as_view(), name='fills-new'),
    # ex: /<root>/fills/1/update/
    url(r'^fills/(?P<pk>[0-9]+)/update/$', fill.FillUpdateView.as_view(), name='fills-update'),
    # ex: /<root>/fills/1/delete/
    url(r'^fills/(?P<pk>[0-9]+)/delete/$', fill.FillDelete.as_view(), name='fills-delete'),

    # ex: /<root>/orders/
    url(r'^orders/$', order.OrderList.as_view(), name='orders-list'),
    # ex: /<root>/orders/5/
    url(r'^orders/(?P<pk>[0-9]+)/$', order.OrderDetailView.as_view(), name='orders-detail'),
    # ex: /<root>/orders/new/
    url(r'^orders/new/$', order.OrderCreate.as_view(), name='orders-new'),
    # ex: /<root>/orders/1/delete/
    url(r'^orders/(?P<pk>[0-9]+)/delete/$', order.OrderDelete.as_view(), name='orders-delete'),
    # ex: /<root>/orders/5/update/
    url(r'^orders/(?P<pk>[0-9]+)/update/$', order.OrderUpdateView.as_view(), name='orders-update'),
    # ex: /<root>/orders/download/
    url(r'^orders/download/$', order.OrderDownloadView.as_view(), name='orders-download'),

    # Autocomplete Input Field In Django Template with Jquery-UI
    # http://blog.appliedinformaticsinc.com/autocomplete-input-field-in-django-template-with-jquery-ui/
    url(r'^autocomplete/asset/$',   autocomplete.AutoCompleteAssetView.as_view(),   name='autocomplete-asset'),
    url(r'^autocomplete/account/$', autocomplete.AutoCompleteAccountView.as_view(), name='autocomplete-account'),

    # ex: /<root>/placements/new/1
    url(r'^placements/new/(?P<order>[0-9]+)$', placement.PlacementCreate.as_view(), name='placements-new'),

]
