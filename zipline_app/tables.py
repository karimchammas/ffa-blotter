import django_tables2 as tables
from .models.zipline_app.order import Order, SHARE
from .forms import OrderForm
from django.utils.html import format_html
from django.utils import timezone
from django.urls import  reverse_lazy
from django_tables2.utils import A  # alias for Accessor

# http://www.andrewtremblay.com/articles/thousands-separator-in-django-tables2/
from django.contrib.humanize.templatetags.humanize import intcomma

class OrderTable(tables.Table):
    fill = tables.Column(verbose_name='Fill')
    user = tables.Column(verbose_name='Placed by')
    make_fill = tables.LinkColumn(
      'zipline_app:fills-new',
      verbose_name='',
      kwargs={'order': A('id')},
      text=lambda record: '' if record.filled() else format_html('<span class="glyphicon glyphicon-copy" title="Place fill for order #{order_id}"></span>', order_id=record.id)
     )
    make_placement = tables.TemplateColumn(template_name='zipline_app/make_placement.html', verbose_name='')
    order_qty = tables.TemplateColumn(
      verbose_name="Nb of shares",
      template_code='{% if record.order_unit!="SHARE" %}{{record.order_qty_unsigned}}{% endif %}',
      orderable=False,
      attrs={"td": {"align": "right"}}
    )
    order_amount = tables.TemplateColumn(
      verbose_name="Amount",
      template_code='{% if record.order_unit=="SHARE" %}{{record.order_qty_unsigned}}{% endif %}',
      orderable=False,
      attrs={"td": {"align": "right"}}
    )
    asset_currency = tables.Column(accessor='asset.asset_currency', verbose_name='Ccy')
    asset = tables.TemplateColumn(template_code='<a href="#" title="{{record.asset.asset_name}} ({{record.asset.asset_origin}})" data-filter-field="asset" data-filter-value="{{record.asset.id}}">{{record.asset.asset_symbol}}</a>')
    account = tables.TemplateColumn(
      template_code='<a href="#" title="{{record.account.account_name}} ({{record.account.account_origin}})" data-filter-field="account" data-filter-value="{{record.account.id}}">{{record.account.account_symbol}}</a>'
    )

    class Meta:
        # copy from https://github.com/bradleyayers/django-tables2/blob/2bf8fd326b697d4e0e4a70ed39aeb3df6ed81865/example/app/tables.py
        # add class="paleblue" to <table> tag
        attrs = {'class': 'table table-bordered table-striped table-hover table-condensed'}
        model = Order
        sequence = OrderForm.field_order + ['fill', 'make_placement', 'make_fill']
        exclude=[
          'order_unit',
          'order_type',
          'limit_price',
          'order_validity',
          'validity_date',
          'order_text',
          'commission',
          'order_qty_unsigned',
          'am_type',
        ]
        fields = OrderForm.field_order + ['fill', 'make_placement', 'make_fill']
        empty_text='No orders are available.'

    def render_pub_date(self, value):
      # https://stackoverflow.com/a/11909289/4126114
      value = timezone.localtime(value)
      return format_html(
        "<span title='%s'>%s</span>" % (
          value.strftime("%Y-%m-%d %I:%M"),
          value.strftime("%m-%d")
        )
      )

    def render_fill(self, record, value):
      out = format_html(
        "<a href='%s'># %s</a> (%s)"%(
          reverse_lazy('zipline_app:fills-detail', args=(value.id,)),
          value.id,
          record.user.username
        )
      )
      return out

    def render_order_qty(self, value, record):
      if record.order_unit==SHARE: return intcomma(record.order_qty_unsigned)
      return ""

    def render_order_amount(self, value, record):
      if record.order_unit!=SHARE: return intcomma(record.order_qty_unsigned)
      return ""

    def render_id(self,value,record):
      out = format_html(
        "<a href='%s' title='%s'># %s%s</a>"%(
          reverse_lazy('zipline_app:orders-detail', args=(record.id,)),
          record.order_text,
          record.id, # value
          ' *' if record.order_text else ''
        )
      )
      return out

