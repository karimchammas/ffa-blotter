# https://github.com/quantopian/zipline/blob/3350227f44dcf36b6fe3c509dcc35fe512965183/zipline/finance/blotter.py#L123
import pandas as pd
from app.polls.matcher import Matcher

#####################################
from zipline.finance.trading import TradingEnvironment
from testfixtures import TempDirectory
import zipline.utils.factory as factory

with TempDirectory() as tempdir:
  env = TradingEnvironment()
  
  # save an asset
  df = pd.DataFrame(
      {  
        "sid":1,
        "exchange":'exchange name',
        "symbol":'a1',
        "asset_name":'a1 name',
      },
      index=[1],
  )
  env.write_data(equities=df)
  
  a1=env.asset_finder.retrieve_asset(sid=1)

  # prepare for data portal
  # from zipline/tests/test_finance.py#L238
  # Note that 2013-01-05 and 2013-01-06 were Sat/Sun
  # Also note that in UTC, NYSE starts trading at 14.30
  # TODO tailor for FFA Dubai
  #  start_date=pd.Timestamp('2013-12-08 9:31AM', tz='UTC'),
  START_DATE = pd.Timestamp('2013-01-07', tz='utc')
  MID_DATE_1 = pd.Timestamp('2013-01-07 15:01', tz='utc')
  MID_DATE_2 = pd.Timestamp('2013-01-07 15:02', tz='utc')
  MID_DATE_3 = pd.Timestamp('2013-01-07 15:03', tz='utc')
  END_DATE = pd.Timestamp('2013-12-31', tz='utc')
  sim_params = factory.create_simulation_parameters(
      start = START_DATE,
      end = END_DATE,
      data_frequency="minute"
  )
  
  from zipline.utils.calendars import get_calendar
  trading_calendar=get_calendar("NYSE")

  from datetime import datetime, timedelta
  #minutes = sim_params.sessions
  #minutes = [pd.Timestamp('2013-01-05 9:01AM', tz='utc')]
  minutes = trading_calendar.minutes_window(
      sim_params.first_open,
      int((timedelta(minutes=1).total_seconds() / 60) * 1)
      + 100)
  print("Minutes: %s" % (minutes))
 
  # Use same sid as for assets above
  # NOT Multiplying by 1000 as documented in zipline/data/minute_bars.py#L419
  fills = {
      1: pd.DataFrame({
  	"open": [3.5, 4.5, 4],
  	"high": [3.5, 4.5, 4],
  	"low": [3.5, 4.5, 4],
  	"close": [3.5, 4.5, 4],
  	"volume": [10, 5, 7],
  	"dt": [MID_DATE_1, MID_DATE_2, MID_DATE_3]
      }).set_index("dt")
  }
  print("data: %s" % (fills))
  
  import os
  #from zipline.data.us_equity_pricing import BcolzDailyBarReader, BcolzDailyBarWriter
  from zipline.data.minute_bars import BcolzMinuteBarReader, BcolzMinuteBarWriter
  
  days = trading_calendar.sessions_in_range(
    trading_calendar.minute_to_session_label(
      minutes[0]
    ),
    trading_calendar.minute_to_session_label(
      minutes[-1]
    )
  )
  print("days: %s" % (days))

  #path = os.path.join(tempdir.path, "testdata.bcolz")
  path = tempdir.path
  writer = BcolzMinuteBarWriter(
    rootdir=path,
    calendar=trading_calendar,
    start_session=days[0],
    end_session=days[-1],
    minutes_per_day=390
  )
  print("Writer session labels: %s" % (writer._session_labels))
  from six import iteritems
  writer.write(iteritems(fills))
  
  print("temp path: %s" % (path))
  equity_minute_reader = BcolzMinuteBarReader(path)
  
  # try to use a data portal
  from zipline.data.data_portal import DataPortal
  dp = DataPortal(
    asset_finder=env.asset_finder,
    trading_calendar=trading_calendar,
    first_trading_day=equity_minute_reader.first_trading_day,
    equity_minute_reader=equity_minute_reader
  )
  
  orders = []

  matcher = Matcher()
  blotter = matcher.orders2blotter(sim_params, env, orders)
  print("Open orders: %s" % (len(blotter.open_orders[a1])))
  
  from zipline._protocol import BarData
  def simulation_dt_func(): return blotter.current_dt
  bd = BarData(
    data_portal=dp,
    simulation_dt_func=simulation_dt_func,
    data_frequency=sim_params.data_frequency,
    trading_calendar=trading_calendar
  )

  all_closed, all_txns = matcher.match_orders_fills(blotter, bd, fills)

  print("========================")
  print("Remaining open")
  #blotter.cancel(o3)
  print("Open orders: %s" % (len(blotter.open_orders[a1])))
  print("Open order status: %s" % ([[o.amount,o.filled,o.open] for o in blotter.open_orders[a1]]))

  print("========================")
  print("All closed orders:")
  for cl in all_closed:
    print(cl)

  print("========================")
  print("All transactions:")
  for txn in [txn.to_dict() for txn in all_txns]:
    print(txn)
