from django.views import generic
from django.contrib import messages
from ...models.zipline_app.placement import Placement
from django.urls import  reverse_lazy
from ...forms import PlacementForm

class PlacementCreate(generic.CreateView):
  model = Placement
  #template_name = 'zipline_app/placement/placement_form.html'
  # fields=['order']
  form_class=PlacementForm

  # short-circuit the GET to lead to POST also
  # No need for logic to check if placement already made for order,
  # since already stated in model.py that field is one-to-one
  def get(self, *args, **kwargs):
    return self.post(*args, **kwargs)

  # cannot move this into form_valid because the "order" field needs to be in a bound form
  def get_form(self, form_class=None):
    return PlacementForm({
      'order': self.kwargs['order']
    })

  # need to keep user in the form_valid function, and cannot move to bound form in `get_form`
  def form_valid(self, form):
    fill = form.save(commit=False)
    if self.request.user.is_authenticated():
      fill.user = self.request.user
    return super(PlacementCreate, self).form_valid(form)

  def get_success_url(self):
    # django message levels
    # https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-levels
    messages.add_message(self.request, messages.INFO, "Successfully created placement: %s" % self.object)
    return reverse_lazy('zipline_app:orders-list')
