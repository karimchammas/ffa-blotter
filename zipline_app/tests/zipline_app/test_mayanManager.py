import datetime
from django.test import TestCase
from django.conf import settings
from ..._mayanManager import MayanManager

class MayanManagerIntegrationTests(TestCase):

    def setUp(self):
      self.mayanMan = MayanManager(
        host=settings.MAYAN_HOST,
        username=settings.MAYAN_ADMIN_USER,
        password=settings.MAYAN_ADMIN_PASSWORD
      )

    # show that it includes tags from 2nd page (since mayan does pagination of results)
    def test_list_doc_by_tag_page_2(self):
      # this particular document is number 11, with pagination for each 10, this doesnt show up without a pagination implementation
      res = self.mayanMan.docs_by_tag('order 160')
      self.assertEquals(
        res,
        [{'id': 17,
          'label': 'FW .msg',
          'url': 'http://pmo.ffaprivatebank.com:8006/api/documents/documents/17/'
        }]
      )


    def test_create_tag_if_not(self):
      # create on tag that already exists
      # but is on 2nd page of "tags()"
      res = self.mayanMan.create_tag_if_not('order 160')
