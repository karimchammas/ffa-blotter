import logging
from ._mfManager import MfManager
from ...models.zipline_app.asset import Asset
from ...models.zipline_app.account import Account
from ...models.zipline_app.custodian import Custodian

# https://docs.djangoproject.com/en/1.10/howto/custom-management-commands/
from django.core.management.base import BaseCommand

import progressbar

logger = logging.getLogger('FFA Dubai blotter')

class Command(BaseCommand):
  help = """Usage:
         python manage.py importMarketflow --help
         python manage.py importMarketflow --debug ...
         python manage.py importMarketflow --origin="MF Dubai" --host=123.123.123.123 --port=123 --user=username --password=mypass --db=database_name
         """

  def add_arguments(self, parser):
    parser.add_argument('--debug',   action='store_true', dest='debug', default=False, help='show higher verbosity')
    parser.add_argument('--origin',  action='store',      dest='origin',required=True, help='set origin field of imported clients, assets, custodians')
    parser.add_argument('--host',    action='store',      dest='host',  required=True, help='ms sql server for marketflow: host IP or name')
    parser.add_argument('--port',    action='store',      dest='port',  required=True, help='ms sql server for marketflow: port number')
    parser.add_argument('--user',    action='store',      dest='user',  required=True, help='ms sql server for marketflow: username')
    parser.add_argument('--password',action='store',  dest='password',  required=True, help='ms sql server for marketflow: password')
    parser.add_argument('--db',      action='store',      dest='db',    required=True, help='ms sql server for marketflow: database name')

  def _handle_assets(self, mfMan, options):
      total = mfMan.assetsCount()
      logger.debug("Django import assets: %s"%total)
      if options['debug']:
        counter = 0
        progress = progressbar.ProgressBar(maxval=total).start()

      for assetMf in mfMan.assetsList():
        if options['debug']:
          counter+=1
          if counter % 100 == 0:
            progress.update(counter)

        # get/create entity/row/case
        #logger.debug("get or create: %s"%asset['TIT_COD'])
        assetDj, created = Asset.objects.update_or_create(
          asset_symbol=assetMf['TIT_COD'],
          defaults={
            'asset_name': assetMf['TIT_NOM'],
            'asset_isin': assetMf['TIT_ISIN_COD'],
            'asset_exchange': 'N/A',
            'asset_currency': assetMf['DEV_SYM_LGE1'],
            'asset_origin': options['origin']
          }
        )
        if created:
          logger.debug("Created asset: %s"%assetDj)
        # Need another "update" flag to identify if updated or not
        #else:
        #  logger.debug("Updated asset: %s"%assetDj)

      if options['debug']:
        progress.finish()

  def _handle_accounts(self, mfMan, options):
      total = mfMan.accountsCount()
      logger.debug("Django import accounts: %s"%total)
      if options['debug']:
        counter = 0
        progress = progressbar.ProgressBar(maxval=total).start()

      for accountMf in mfMan.accountsList():
        if options['debug']:
          counter+=1
          if counter % 100 == 0:
            progress.update(counter)

        # get/create entity/row/case
        accountDj, created = Account.objects.update_or_create(
          account_symbol=accountMf['CLI_COD'],
          defaults={
            'account_name': accountMf['CLI_NOM_PRE'],
            'account_origin': options['origin']
          }
        )

        if created:
          logger.debug("Created account: %s"%accountDj)

      if options['debug']:
        progress.finish()


  def _handle_custodians(self, mfMan, options):
      total = mfMan.custodiansCount()
      logger.debug("Django import custodians: %s"%total)
      if options['debug']:
        counter = 0
        progress = progressbar.ProgressBar(maxval=total).start()

      for custodianMf in mfMan.custodiansList():
        if options['debug']:
          counter+=1
          if counter % 100 == 0:
            progress.update(counter)

        # get/create entity/row/case
        #logger.debug("get or create: %s"%custodian['TIT_COD'])
        custodianDj, created = Custodian.objects.update_or_create(
          custodian_symbol=custodianMf['ENT_COD'],
          defaults={
            'custodian_name': custodianMf['ENT_FULL_NAME'],
            'custodian_origin': options['origin']
          }
        )
        if created:
          logger.debug("Created custodian: %s"%custodianDj)

      if options['debug']:
        progress.finish()

  def handle(self, *args, **options):
    h1 = logging.StreamHandler(stream=self.stderr)
    logger.addHandler(h1)
    if options['debug']:
      logger.setLevel(logging.DEBUG)

    with MfManager(host=options['host'], port=options['port'], user=options['user'], password=options['password'], db=options['db']) as mfMan:
      self._handle_assets(mfMan, options)
      self._handle_accounts(mfMan, options)
      self._handle_custodians(mfMan, options)
