## Changelog
See also [TODO](TODO.md)

## [ ] Version 1.1
- [ ] simplify the side-by-side view `get_combined` function since now only dedicated fills are supported
- [x] run the `OrderManager.process` function at each page load
  - alternatives could have been: cron it; use django's cellery to schedule it as a repeated job

## [x] Version 1.0
- [x] Removed the zipline engine altogether from the `ffa-blotter` repository
  - in FFA, there was no need at all for automatic matching of orders with fills
  - also, the zipline engine integration was challenging to maintain
  - Only keeping a one-to-one relationship between orders and fills
  - i.e. there are no partial fills, nor extra fills, only exact fills
  - i.e. the dedicated fills
- [x] spin off repository `ffa-blotter` from the original `django-zipline`
  - rename the original to `django-zipline-2` to maintain the redirection on github to `ffa-blotter`

## [x] Version 0.3
I didn't maintain the changelogs very well for a while

- [x] send emails using NTLM backend

## [x] Version 0.2
I didn't maintain the changelogs very well for a while

## [x] Version 0.1
I didn't maintain the changelogs very well for a while

## [x] Version 0.0.2
- [x] travis-ci.org
- [x] no need to update zlmodel upon asset changes
- [x] nav bar active page should be changed with jquery upon page load
- [x] UX
  - [x] rename "symbol" on index to "asset" (show name using tooltip?)
  - create in index
    - [x] in-page create account: send django message upon create
    - [x] replace all inline creates with divs that show up when clicking on add new order/fill
      - [x] not to be "bootstrap modal" because user needs to keep sight of orders/fills (same reason why not just going to a new page completely)
      - [x] use same concept as one-line create, but make the form take the whole page width (instead of displaying the order form on the left and the fill form on the right)
      - [x] quantity input too small
      - [x] asset add button unintuitive
      - [x] symbol dropdown is too small
      - [x] send django message when asset/account/order/fill created from index
        - [x] ~~how do multiple django messages sent in one request get displayed?~~
          - I dont have this case ATM
        - [x] also when order/fill deleted
          - assets/accounts to be dealt with separately since they''re not in direct display on the index page (possibly think of a "clean up" button)

- [x] ~~bug: create order at t1, then create at `t2>t1`, then drop the one at t1, but the minute t1 is still there in combined view~~
  - I couldnt reproduce this bug anymore .. so cancelling
- [x] ~~test failing for in-page create account~~
  - doesnt seem to fail anymore
- [x] fill quantity too large yields error: Python int too large to convert to SQLite INTEGER
- [x] more index
  - [x] edit in details
    - this is related to drafting (in version 0.1.1) .. so not sure if should postpone
  - [x] delete buttons are ugly and overlap with timestamp
  - [x] ~~add column explicitly calculated for pending quantities~~
    - display a summary of pending quantities per asset
- [x] bug: when unused fills are negative, they dont show up
- [x] fill price cannot be negative (zipline constraint)
- [x] bug: create fill with qty 0 yields error
- [x] time zones!
  - times not displayed in beirut timezone
  - ~~omitting timezones would yield django error about timezone-naive timestamp uncomparable to timezone-aware timestamp~~
- [x] add section "XX fills required to close open orders"
- [x] replace heart with github logo/link


## [x] Version 0.0.1
- [x] django app from tutorial customized to blotter
- [x] use zipline as matching enging
- [x] integrate zipline into django app
- [x] display average price (in red like filled) in original orders view
- [x] original order details page to show transactions filling order
- [x] add nav header
- [x] change architecture of running matching engine: currently re-run if needed on every request
  - change to adding a class with methods `{add,edit,delete}_{order,fill}` being static
  - this class should use [django signals](https://docs.djangoproject.com/en/1.10/ref/signals/):
    - `connection_created` for an initial load of what is in the database (existing `ZlModel.update`)
    - `post_init` for adding orders/fills/assets
    - `post_save` for editing
    - `post_delete` for deleting
- [x] handle more than just asset A1 (WIP .. currently crashes if two assets added, one order per asset added, and then fill added for 2nd asset)
- [x] matcher: test that fills before an order do not fill it
- [x] add account symbols attached to orders
- [x] UX with [django-bootstrap3](https://github.com/dyve/django-bootstrap3)
  - [x] nav header contrasted with white background
  - [x] side-by-side view: asset, order, fill
  - [x] tabular for printing
- [x] rename project to django-zipline
- [x] move files to match structure of zipline
- [x] new asset: works with generic view form and bootstrap form (was submitting form with jquery but violating csrf)
- [x] ~~add an intermediate "bar data" model between fills and ZlModel to reduce computations~~
  - cancelled since the weighted average close would still require re-computation
- [x] aggregate fills per asset by minute in chopSeconds
- [x] index page
  - [x] order create in page and redirect back to index
  - [x] fill  create in page and redirect back to index
  - [x] asset create in page and redirect back to index
  - [x] delete in page and redirect back to index
  - [x] ~~edit inline~~ link to details in order to edit
- [x] new asset form should check that symbol is not already defined
  - this is a zipline constraint
  - ~~or maybe just open the admin?~~
- [x] bug: if no open orders on A1 and new fill on A1, not getting alerted about unused fill
