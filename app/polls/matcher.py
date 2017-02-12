import numpy
import pandas as pd

# initialize blotter
from zipline.finance.blotter import Blotter
#from zipline.finance.slippage import FixedSlippage
#slippage_func = FixedSlippage(spread=0.0)
from zipline.finance.slippage import VolumeShareSlippage

# try to use a data portal
from zipline.data.data_portal import DataPortal
from zipline._protocol import BarData

# fills2reader
from datetime import datetime, timedelta
from six import iteritems
import os
#from zipline.data.us_equity_pricing import BcolzDailyBarReader, BcolzDailyBarWriter
from zipline.data.minute_bars import BcolzMinuteBarReader, BcolzMinuteBarWriter
from functools import reduce

# constructor
from zipline.utils.calendars import get_calendar
from zipline.finance.trading import TradingEnvironment
import zipline.utils.factory as factory

class Matcher:
  def __init__(self):
    self.env = TradingEnvironment()
    
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
    self.env.write_data(equities=df)
    
    # prepare for data portal
    # from zipline/tests/test_finance.py#L238
    # Note that 2013-01-05 and 2013-01-06 were Sat/Sun
    # Also note that in UTC, NYSE starts trading at 14.30
    # TODO tailor for FFA Dubai
    #  start_date=pd.Timestamp('2013-12-08 9:31AM', tz='UTC'),
    START_DATE = pd.Timestamp('2013-01-07', tz='utc')
    END_DATE = pd.Timestamp(datetime.now(), tz='utc')
    self.sim_params = factory.create_simulation_parameters(
        start = START_DATE,
        end = END_DATE,
        data_frequency="minute"
    )
    
    self.trading_calendar=get_calendar("NYSE")

  def fills2minutes(self,fills):
    minutes = [sid.index.values for _, sid in fills.items()]
    minutes = reduce(lambda a, b: a.concatenate(b), minutes, [])
    minutes = [pd.Timestamp(x, tz='utc') for x in minutes]
    minutes.sort()
    minutes = list(set(minutes))
    return minutes

  def fills2reader(self, tempdir, minutes, fills):
    print("minutes",minutes)
    for _,fill in fills.items():
      fill["open"] = fill["close"]
      fill["high"] = fill["close"]
      fill["low"]  = fill["close"]

    days = self.trading_calendar.sessions_in_range(
      self.trading_calendar.minute_to_session_label(
        minutes[0]
      ),
      self.trading_calendar.minute_to_session_label(
        minutes[-1]
      )
    )
    print("days: %s" % (days))
  
    #path = os.path.join(tempdir.path, "testdata.bcolz")
    path = tempdir.path
    writer = BcolzMinuteBarWriter(
      rootdir=path,
      calendar=self.trading_calendar,
      start_session=days[0],
      end_session=days[-1],
      minutes_per_day=390
    )
    print("Writer session labels: %s" % (writer._session_labels))
    writer.write(iteritems(fills))
    
    print("temp path: %s" % (path))
    reader = BcolzMinuteBarReader(path)

    # get array of timestamps
    columns = ['open', 'high', 'low', 'close', 'volume']
    arrays = list(map(numpy.transpose, reader.load_raw_arrays(
      columns, minutes[0], minutes[-1], [1],
    )))
    print('arrays',arrays)

    return reader

  def orders2blotter(self, orders):
    slippage_func = VolumeShareSlippage(
      volume_limit=1,
      price_impact=0
    )
    blotter = Blotter(
      data_frequency=self.sim_params.data_frequency,
      asset_finder=self.env.asset_finder,
      slippage_func=slippage_func
    )
    
    print("Place orders")
    orders2 = []
    for order in orders:
      blotter.set_date(order["dt"])
      print(blotter.current_dt)
      #print("Order a1 +10")
      #o1=
      blotter.order(order["sid"],order["amount"],order["style"])

    print("Open orders: %s" % ({k.symbol: len(v) for k,v in iteritems(blotter.open_orders)}))
    return blotter

  def blotter2bardata(self, equity_minute_reader, blotter):
    dp = DataPortal(
      asset_finder=self.env.asset_finder,
      trading_calendar=self.trading_calendar,
      first_trading_day=equity_minute_reader.first_trading_day,
      equity_minute_reader=equity_minute_reader
    )

    def simulation_dt_func(): return blotter.current_dt
    bd = BarData(
      data_portal=dp,
      simulation_dt_func=simulation_dt_func,
      data_frequency=self.sim_params.data_frequency,
      trading_calendar=self.trading_calendar
    )

    return bd

  def match_orders_fills(self, blotter, bar_data, all_minutes, fills):
    all_closed = []
    all_txns = []
    for dt in all_minutes:
        print("========================")
        dt = pd.Timestamp(dt, tz='utc')
        blotter.set_date(dt)
        print("use data portal to dequeue open orders: %s" % (blotter.current_dt))
        new_transactions, new_commissions, closed_orders = blotter.get_transactions(bar_data)
      
  #      print("Closed orders: %s" % (len(closed_orders)))
  #      for order in closed_orders:
  #        print("Closed orders: %s" % (order))
  #    
  #      print("Transactions: %s" % (len(new_transactions)))
  #      for txn in new_transactions:
  #        print("Transactions: %s" % (txn.to_dict()))
  #    
  #      print("Commissions: %s" % (len(new_commissions)))
  #      for txn in new_commissions:
  #        print("Commissions: %s" % (txn))
      
        blotter.prune_orders(closed_orders)
        #print("Open orders: %s" % (len(blotter.open_orders[a1])))
        #print("Open order status: %s" % ([o.open for o in blotter.open_orders[a1]]))
  
        all_closed = numpy.concatenate((all_closed,closed_orders))
        all_txns = numpy.concatenate((all_txns, new_transactions))

    return all_closed, all_txns 
