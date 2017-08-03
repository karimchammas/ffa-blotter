from django.test import TestCase
from django.urls import reverse
from ...models.zipline_app.fill import Fill
from ...models.zipline_app.side import BUY, SELL
from .test_fill import FillBaseTests
from io import BytesIO
import pandas as pd
from ...utils import myTestLogin

class BlotterDownloadViewsTests(FillBaseTests):
  def test_get(self):
    # o1 is already created in setUp as self.o1
    o2 = self.create_order_default(order_text="random order 2", days=-2, order_qty_unsigned=20)
    o3 = self.create_order_default(order_text="random order 3", days=-3, order_qty_unsigned=30)
    f3 = self.create_fill_from_order_default(order=o3, fill_price=3, fill_text="fill 3")

    # django test file download
    # http://stackoverflow.com/a/39655502/4126114
    url = reverse('zipline_app:blotter-download')
    response = self.client.get(url, follow=True)
    content = BytesIO(b"".join(response.streaming_content))

    # How to read a .xlsx file using the pandas Library in iPython
    # http://stackoverflow.com/questions/16888888/ddg#16896091
    xl_file = pd.ExcelFile(content)
    dfs = {sheet_name: xl_file.parse(sheet_name) 
              for sheet_name in xl_file.sheet_names}

    # my tests
    self.assertTrue('blotter' in dfs)
    self.assertEqual(len(dfs['blotter']),3)

    self.assertEqual(dfs['blotter']['Status'].tolist(), ['working', 'working', 'filled'])

    # check in order
    df = dfs['blotter']
    self.assertEqual(df[df['Ref']==1]['Status'].tolist()[0], 'working')
    self.assertEqual(df[df['Ref']==2]['Status'].tolist()[0], 'working')
    self.assertEqual(df[df['Ref']==3]['Status'].tolist()[0], 'filled')
