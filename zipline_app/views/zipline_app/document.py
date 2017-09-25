from django.views import generic
from ...models.zipline_app.order import Order

from ...forms import OrderDocumentForm
from django.urls import  reverse_lazy

from django.http import HttpResponseRedirect


from ..._mayanManager import MayanManager

class DocumentDownloadView(generic.ListView):
  def get(self, *args, **kwargs):
    mayanMan = MayanManager(
      host=settings.MAYAN_HOST,
      username=settings.MAYAN_ADMIN_USER,
      password=settings.MAYAN_ADMIN_PASSWORD
    )
    return mayanMan.download_doc(kwargs['pk'])

from django.conf import settings
class OrderDocumentUploadView(generic.edit.FormView):
  template_name = 'zipline_app/order/order_document_upload.html'
  form_class = OrderDocumentForm
  
  def get_success_url(self):
    order_id = self.kwargs['pk']
    return reverse_lazy('zipline_app:orders-detail', args=(order_id,))

  # need to append 'order' in case of form failure, so that "order.id" in the order_document_upload.html is not empty
  def get_context_data(self, **kwargs):
    context = super(OrderDocumentUploadView, self).get_context_data(**kwargs)
    context['order'] = Order.objects.get(id=self.kwargs['pk'])
    context['docs_form'] = OrderDocumentForm()
    return context

  def post(self, request, *args, **kwargs):
    #username = None
    if not request.user.is_authenticated():
      raise Exception("Access denied")
    #username = request.user.username

    order_id = self.kwargs['pk']
    if not order_id:
      raise Exception("Submitting form without order id")

    form_class = self.get_form_class()
    form = self.get_form(form_class)
    files = request.FILES.getlist('docfile')
    if form.is_valid():
      mayanMan = MayanManager(
        host=settings.MAYAN_HOST,
        username=settings.MAYAN_ADMIN_USER,
        password=settings.MAYAN_ADMIN_PASSWORD
      )
      if mayanMan.api is None:
        raise Exception("Failed to connect to mayan edms")

      tag_label = mayanMan.order_id_to_tag(order_id)
      tag_obj = mayanMan.create_tag_if_not(tag_label)
      doc_ids = []
      for f in files:
        response = mayanMan.upload_doc(f, tag_obj)
        doc_ids.append(response['id'])

      mayanMan.attach_docs_to_tag(tag_obj, doc_ids)
      return self.form_valid(form)
    else:
      return self.form_invalid(form)


def delete_doc_view(request, order_id, doc_id):
  if not request.user.is_authenticated():
    raise Exception("Access denied")

  mayanMan = MayanManager(
    host=settings.MAYAN_HOST,
    username=settings.MAYAN_ADMIN_USER,
    password=settings.MAYAN_ADMIN_PASSWORD
  )

  mayanMan.delete_doc(doc_id)

  url = reverse_lazy('zipline_app:orders-detail', args=(order_id,))
  return HttpResponseRedirect(url)

