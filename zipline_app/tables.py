import django_tables2 as tables
from .models.zipline_app.order import Order
from .forms import OrderForm
from django.utils.html import format_html
from django.utils import timezone
from django.urls import  reverse_lazy
from django_tables2.utils import A  # alias for Accessor

class OrderTable(tables.Table):
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

    class Meta:
        model = Order
        # add class="paleblue" to <table> tag
        attrs = {'class': 'paleblue'}
        sequence = ['id', 'user', 'order_status'] + OrderForm.field_order + ['fill', 'make_fill', 'make_placement']
        fields = OrderForm.field_order + ['id', 'user', 'order_status', 'fill', 'make_fill', 'make_placement']
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
