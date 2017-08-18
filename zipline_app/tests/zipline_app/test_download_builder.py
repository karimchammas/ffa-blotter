from django.test import TestCase
from .test_zipline_app import OrderBaseTests
from ...models.zipline_app.side import BUY
from ...download_builder import DownloadBuilder
from pandas import DataFrame
import tempfile
from os.path import exists
from django.http import FileResponse

class DownloadBuilderTests(OrderBaseTests):
  def setUp(self):
    super(DownloadBuilderTests, self).setUp()
    self.builder = DownloadBuilder()

  def test_orders2df(self):
    o1 = self.create_order_default(order_text="random order 1", days=-1, order_qty_unsigned=10)
    o2 = self.create_order_default(order_text="random order 2", days=-2, order_qty_unsigned=20)
    o3 = self.create_order_default(order_text="random order 3", days=-3, order_qty_unsigned=30)

    orders = [o1, o2, o3]
    df = self.builder.orders2df(orders)
    self.assertTrue(isinstance(df, DataFrame))

  def test_df2xlsx(self):
    df = self.builder.empty_df()
    full_name = self.builder.df2xlsx(df)
    self.assertNotEqual(full_name, None)
    self.assertEqual(exists(full_name),1)

  def test_fn2response(self):
    with tempfile.NamedTemporaryFile() as fn:
      response = self.builder.fn2response(fn.name)
      self.assertTrue(isinstance(response, FileResponse))

