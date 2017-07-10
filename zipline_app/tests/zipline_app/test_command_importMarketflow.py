from django.test import TestCase
from unittest.mock import patch

# Testing management commands
# https://docs.djangoproject.com/en/1.10/topics/testing/tools/#management-commands
from django.core.management import call_command
from django.utils.six import StringIO

class ImportMarketflowCommandTests(TestCase):
  def setUp(self):
    patcher = patch('zipline_app.management.commands.importMarketflow.MfManager')
    self.addCleanup(patcher.stop)
    mock = patcher.start()
    instance = mock.return_value.__enter__.return_value
    instance.assetsList.return_value = [
      {'TIT_COD':'asset 1', 'TIT_NOM':'name of asset 1', 'TIT_ISIN_COD': 'ISIN 1', 'DEV_SYM_LGE1': 'USD'},
      {'TIT_COD':'asset 2', 'TIT_NOM':'name of asset 2', 'TIT_ISIN_COD': 'ISIN 2', 'DEV_SYM_LGE1': 'USD'},
    ]
    instance.assetsCount.return_value = 2

    instance.accountsList.return_value = [
      {'CLI_COD':'account 1', 'CLI_NOM_PRE':'name of account 1'},
      {'CLI_COD':'account 2', 'CLI_NOM_PRE':'name of account 2'},
    ]
    instance.accountsCount.return_value = 2

    instance.custodiansList.return_value = [
      {'CLI_COD':'custodian 1', 'CLI_NOM_PRE':'name of custodian 1'},
      {'CLI_COD':'custodian 2', 'CLI_NOM_PRE':'name of custodian 2'},
    ]
    instance.custodiansCount.return_value = 2

  def testMain(self):
    with StringIO() as out, StringIO() as err:
      call_command('importMarketflow', '--host=bla', '--port=123', '--user=bla', '--password=bla', '--db=bla', '--origin=bli', stderr=err, stdout=out, debug=True)
      self.assertIn('Django import', err.getvalue())

