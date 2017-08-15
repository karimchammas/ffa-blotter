import django_tables2 as tables
from .models.zipline_app.order import Order, SHARE
from .forms import OrderForm
from django.utils.html import format_html
from django.utils import timezone
from django.urls import  reverse_lazy
from django_tables2.utils import A  # alias for Accessor

# copy from https://github.com/bradleyayers/django-tables2/blob/2bf8fd326b697d4e0e4a70ed39aeb3df6ed81865/example/app/tables.py
class BootstrapTable(tables.Table):
  class Meta:
    attrs = {'class': 'table table-bordered table-striped table-hover'}

class OrderTable(BootstrapTable):
    fill = tables.Column(verbose_name='Fill')
    # https://stackoverflow.com/q/6157101/4126114
    id = tables.LinkColumn(
      'zipline_app:orders-detail',
      args=(A('id'),),
      text=lambda record: '# %s'%(record.id)
    )
    make_fill = tables.LinkColumn(
      'zipline_app:fills-new',
      verbose_name='',
      kwargs={'order': A('id')},
      text=lambda record: '' if record.filled() else format_html('<span class="glyphicon glyphicon-copy" title="Place fill for order #%s"></span>'%(record.id))
     )
    make_placement = tables.TemplateColumn(template_name='zipline_app/make_placement.html', verbose_name='')
    order_qty = tables.TemplateColumn(verbose_name="Nb of shares", template_code='{% if record.order_unit!="SHARE" %}{{record.order_qty_unsigned}}{% endif %}', orderable=False)
    order_amount = tables.TemplateColumn(verbose_name="Amount", template_code='{% if record.order_unit=="SHARE" %}{{record.order_qty_unsigned}}{% endif %}', orderable=False)
    asset_currency = tables.Column(accessor='asset.asset_currency', verbose_name='Ccy')

    class Meta:
        model = Order
        # add class="paleblue" to <table> tag
        #attrs = {'class': 'bootstrap'}
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        sequence = OrderForm.field_order + ['fill', 'make_fill', 'make_placement']
        exclude=[
          'order_unit',
          'order_status',
          'order_type',
          'limit_price',
          'order_validity',
          'validity_date',
          'order_text',
          'commission',
          'order_qty_unsigned',
          'am_type',
        ]
        fields = OrderForm.field_order + ['fill', 'make_fill', 'make_placement']
        empty_text='No data'

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
        "<a href='%s'># %s</a>"%(
          reverse_lazy('zipline_app:fills-detail', args=(value.id,)),
          value.id
        )
      )
      return out

    def render_order_qty(self, value, record):
      if record.order_unit==SHARE: return record.order_qty_unsigned
      return ""

    def render_order_amount(self, value, record):
      if record.order_unit!=SHARE: return record.order_qty_unsigned
      return ""
