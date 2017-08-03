from django.views import generic
from django.contrib import messages
from ...models.zipline_app.placement import Placement
from django.urls import  reverse_lazy

class PlacementCreate(generic.CreateView):
  model = Placement
  #template_name = 'zipline_app/placement/placement_form.html'
  fields=['order']

  def form_valid(self, form):
    placement = form.save(commit=False)
    if self.request.user.is_authenticated():
      placement.user = self.request.user
    return super(PlacementCreate, self).form_valid(form)

  def get_success_url(self):
    # django message levels
    # https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-levels
    messages.add_message(self.request, messages.INFO, "Successfully created placement: %s" % self.object)
    return reverse_lazy('zipline_app:blotter-concealed')
