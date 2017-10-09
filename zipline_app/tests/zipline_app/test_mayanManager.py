import datetime
from django.test import TestCase
from django.conf import settings
from ..._mayanManager import MayanManager

class MayanManagerTests(TestCase):
    # show that it includes tags from 2nd page (since mayan does pagination of results)
    def test_list_doc_by_tag_page_2(self):
      mayanMan = MayanManager(
        host=settings.MAYAN_HOST,
        username=settings.MAYAN_ADMIN_USER,
        password=settings.MAYAN_ADMIN_PASSWORD
      )
      # this particular document is number 11, with pagination for each 10, this doesnt show up without a pagination implementation
      res = mayanMan.docs_by_tag('order 160')
      self.assertEquals(
        res,
        [{'id': 17,
          'label': 'FW .msg',
          'url': 'http://pmo.ffaprivatebank.com:8006/api/documents/documents/17/'
        }]
      )
