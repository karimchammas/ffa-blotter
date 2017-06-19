
## [ ] Version 0.1.1
- [ ] move the matching engine to use redis backend
  - something like what is described [here](https://channels.readthedocs.io/en/stable/getting-started.html#running-with-channels)
- [ ] sort by "open" first then by date (remember that main view will be for one day)
- [ ] how about an "email" order button? possibly rename `vote` field and button
- [ ] email notification on order/fill
- [ ] select day on top and show orders/fills for one day
- [ ] alert about eariler days with open orders or unused fills
    - use top right like github alerts?
    - or show side bar like travis?
    - or `django.contrib.messages`?
- [ ] add MF asset name + account name
- [ ] use pusher?
- [ ] broker can edit/delete his/her own fills/orders
- [ ] take frequency up to seconds from minutes (and remove chopSeconds)
  - otherwise constrain the django fields for `pub_date` to be without seconds
  - also default for order `pub_date` to be now (like fill `pub_date`)
- [ ] could also add [django-review](https://github.com/bitlabstudio/django-review)
- [ ] place an order "draft" to allow placing multiple orders and then single-button "publish drafted"
  - allow a user to edit/delete an order only when still a draft
  - same for fills?
  - how are cancels related?
- [ ] unused fills, if closed with correction fills, no longer show up anywhere (as slippage?)
  - or probably should compute slippage from asset''s close?
  - this would require close data (linked from the asset symbol)
  - the symbol would need to be a valid "yahoo finance", "google finance", "blooomberg", "marketflow" symbol
- [ ] delete should be open only to an admin user
  - [ ] add undo for accidental deletes (or display history somewhere)
    - do I still need this if it is only open to an admin user?
    - there will be a "cancel order" button for regular users (which can be followed by a delete)
- [ ] make asset exchange foreign key and display alert if ordering/filling during exchange closed time

## [ ] Version 0.1.0
- [ ] release


## [ ] Version 0.0.3
- [ ] replace dropdowns with [autocomplete](https://github.com/yourlabs/django-autocomplete-light/)
  - or maybe just vanilla [jquery ui](https://jqueryui.com/resources/demos/autocomplete/combobox.html)
- [ ] host on heroku using free dyno hours?
  - will require moving the database to postgres
  - https://devcenter.heroku.com/articles/free-dyno-hour-faq
  - https://devcenter.heroku.com/articles/getting-started-with-python#introduction
  - or azure?
  - https://blogs.msdn.microsoft.com/matt-harrington/2014/04/18/how-to-host-your-django-apps-on-azure-for-free/
- [ ] link fills to transactions/orders
  - but `fills_as_dict_df` loses the original IDs (check `test_fills_as_dict_df`)
  - but transactions have no reference from zipline to the fills
  - can it be done by using the asset/timestamp pair as key?
- [ ] username/password
  - single sign-on? (use ldap?)
- [ ] add broker field
- [ ] what about GTC orders and cancel on EOD
- [ ] default landing page at `/`
  - think of github dashboard
  - redirect to log in if not logged in
  - how to manage authentication / authorization
- [ ] how to move to async? Decide between
  - probably no need as of now since the matching engine needs to be re-run completely anyway
  - [django-angular](http://django-angular.readthedocs.io/en/latest/angular-model-form.html)
  - [django-channels](https://channels.readthedocs.io/en/stable/concepts.html)
- [ ] rename my `order_text` and `fill_text` to `...comment`
- [ ] what happens if i delete an account which is referenced in an order
  - [ ] same for asset
- [ ] index in-page create buttons: add way to close them without reloading
- [ ] during loading of page after asset create, block page (display "loading...")
  - might also want to automatically re-open modals if for example the new-fill modal was opened followed by the new-asset modal
- [ ] favicon.ico
- [ ] use order vote as order close
- [ ] fill from index required fills per asset
- [ ] bug: fill that gets its timestamp changed to the same as another fill, then changed back out of that timestamp, disappears from the combined view
- [ ] order list, fills list: order by desc `pub_date`
- [ ] if fill entered before/after order, make it easy to re-attach to order timestamp
- [ ] add "order status" flag: working, closed, ...
  - or should this be implied from the data? (with the default always being "working")
- [ ] inline alert of unmatched fills in side-by-side view has a popup that could display the number of unused fills
  - would this replace the separate section?
- [ ] how to handle the index table when data becomes too much
  - how to truncate the data (do not show past orders that were filled, or past fills that completed an order)
  - keep showing open orders or unused fills
  - etc
- [ ] drop redundant load of css/js from html templates, except base.html
  ```
  {# Load CSS and JavaScript #}
  {% bootstrap_css %}
  {% bootstrap_javascript %}
  ```
