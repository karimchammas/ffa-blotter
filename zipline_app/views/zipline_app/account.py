from django.urls import  reverse_lazy
from django.views import generic
from django.contrib import messages
from ...models.zipline_app.account import Account
from ...utils import redirect_index_or_local

class AccountCreate(generic.CreateView):
  model = Account
  fields = ['account_symbol', 'account_name']
  template_name = 'zipline_app/account/account_form.html'

  def get_success_url(self):
    messages.add_message(self.request, messages.INFO, "Successfully created account: %s" % self.object)
    return redirect_index_or_local(self,'zipline_app:accounts-list')

# inheriting from create+get_context with account_list instead of inheriting from listview
# so that I can have the inline in create
# http://stackoverflow.com/a/12883683/4126114
class AccountList(generic.ListView):
  template_name = 'zipline_app/account/account_list.html'
  context_object_name='account_list'

  def get_queryset(self):
    return Account.objects.all()

class AccountDelete(generic.DeleteView):
    model = Account
    success_url = reverse_lazy('zipline_app:accounts-list')
    template_name = 'zipline_app/account/account_confirm_delete.html'

class AccountDetailView(generic.DetailView):
    model = Account
    template_name = 'zipline_app/account/account_detail.html'

class AccountUpdateView(generic.UpdateView):
  model = Account
  fields = ['account_symbol', 'account_name']
  template_name = 'zipline_app/account/account_form.html'

  def get_success_url(self):
    # django message levels
    # https://docs.djangoproject.com/en/1.10/ref/contrib/messages/#message-levels
    messages.add_message(self.request, messages.INFO, "Successfully updated account: %s" % self.object)
    return redirect_index_or_local(self,'zipline_app:accounts-list')

