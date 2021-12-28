import unittest
from unittest.mock import patch
import json, re

from httpd_site import ManagePage, GeneratorPage
from twisted.web.test.test_web import DummyRequest

import settings

settings.DOMAINS = ['localhost']
import setup_db


class TestGeneratePage(unittest.TestCase):
    def test_generate_POST(self):
        request = DummyRequest([''])

        default_args = {
            'sql_server_trigger_name': ['TRIGGER1'],
            'email': ['email@fake.fake'],
            'sql_server_view_name': ['VIEW1'],
            'memo': ['test'],
            'webhook': [''],
            'sql_server_function_name': ['FUNCTION1'],
            'redirect_url': [''],
            'type': ['web'],
            'sql_server_table_name': ['TABLE1'],
            'fmt': [''],
            'clonedsite': ['']
        }

        for input_type, args in [("string", default_args), ("bytes", {k.encode('utf-8'): [v[0].encode('utf-8')] for k,v in default_args.items()})]:
            with self.subTest(input_type=input_type):
                request.args = args

                request.method = 'POST'

                result = GeneratorPage().render(request)
                actual_result = json.loads(result)

                assert "Auth" in actual_result

                assert "Token" in actual_result
                assert re.match("^http://localhost/.*/{}/.*$".format(actual_result["Token"]), actual_result["Url"])
                assert re.match("^{}\.localhost$".format(actual_result["Token"]), actual_result["Hostname"])

                assert len(actual_result["Url_components"]) == 3
                assert actual_result["Url_components"][0] == ["http://localhost"]
                assert sorted(actual_result["Url_components"][1]) == ["about", "articles", "feedback", "images", "static",
                                                                      "tags", "terms", "traffic"]
                assert sorted(actual_result["Url_components"][2]) == ["contact.php", "index.html", "post.jsp", "submit.aspx"]

                assert actual_result["Error"] is None
                assert actual_result["Error_Message"] is None
                assert actual_result["Email"] == "email@fake.fake"

# class TestManagePage(unittest.TestCase):
#
#     @patch("redismanager.db.hgetall")
#     def test_render_GET(self, mock_hgetall):
#         mock_hgetall.return_value = {
#             'type': 'web',
#             'email': 'email@fake.fake',
#             'webhook': '',
#             'fmt': '',
#             'memo': 'test',
#             'clonedsite': '',
#             'sql_server_table_name': 'TABLE1',
#             'sql_server_view_name': 'VIEW1',
#             'sql_server_function_name': 'FUNCTION1',
#             'sql_server_trigger_name': 'TRIGGER1',
#             'redirect_url': ''
#         }
#
#         request = DummyRequest([''])
#         request.args = {
#             b'token': 'x',
#             b'auth': 'y'
#         }
#         result = ManagePage().render(request)
#         self.assertEqual(True, False)  # add assertion here
#         return "x"
