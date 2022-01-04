from twisted.trial.unittest import TestCase
import json, re, io, os, copy

from twisted.python.modules import getModule

thisModule = getModule(__name__)
dataPath = thisModule.filePath.parent().parent()

os.environ["CANARY_WEB_IMAGE_UPLOAD_PATH"] = dataPath.child("tests").child("uploads").path
os.environ["CANARY_WG_PRIVATE_KEY_SEED"] = "iti59nUKwKrE1jbM8scQ4TvQCLCvSXvnW5PO3g8DLLE\\\\\\="
os.environ["CANARY_TEMPLATE_DIR"] = dataPath.child("templates").path
os.environ["CANARY_TEST_REDIS"] = "True"

from PIL import Image, ImageChops

from httpd_site import ManagePage, GeneratorPage
from twisted.web.test.test_web import DummyRequest
from twisted.web.http_headers import Headers

import settings
import random

from queries import get_canarydrop

settings.DOMAINS = ['localhost']
import setup_db


def encode_form(args):
    """
    Encodes two form values and a fake image file as multipart form encoding.
    """
    random_chars = [str(random.randrange(10)) for _ in range(28)]
    boundary = b"------" + "".join(random_chars).encode('utf-8')

    lines = [boundary]

    def add(name, content, is_image=False, filename="img.jpeg", content_type="image/jpeg"):
        header = "Content-Disposition: form-data; name={}".format(name)
        if is_image:
            header += "; filename={}".format(filename)
            header += "\r\nContent-Type: {}".format(content_type)
        lines.extend([header.encode('utf-8'), b"", content, b"", boundary])

    for k, v in args.items():
        add(
            k,
            v[0][1].read() if k == "web_image" else v[0].encode('utf-8'),
            is_image=(k == "web_image"),
            filename=v[0][0] if k == "web_image" else "",
            content_type=v[0][2] if k == "web_image" else ""
        )

    # add("f", f.read(), isImage=True)

    lines.extend([boundary + b"--", b""])
    return boundary[2:], b"\r\n".join(lines)


class TestGeneratePage(TestCase):
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

    def assert_generate_result_ok(self, result):

        assert "Auth" in result
        assert "Token" in result

        assert re.match("^http://localhost/.*/{}/.*$".format(result["Token"]), result["Url"])
        assert re.match("^{}\.localhost$".format(result["Token"]), result["Hostname"])

        assert len(result["Url_components"]) == 3
        assert result["Url_components"][0] == ["http://localhost"]
        assert sorted(result["Url_components"][1]) == ["about", "articles", "feedback", "images",
                                                       "static",
                                                       "tags", "terms", "traffic"]
        assert sorted(result["Url_components"][2]) == ["contact.php", "index.html", "post.jsp",
                                                       "submit.aspx"]

        assert result["Error"] is None
        assert result["Error_Message"] is None
        assert result["Email"] == "email@fake.fake"

        assert list(result.keys()) == ['Error', 'Error_Message', 'Url', 'Url_components', 'Token', 'Email', 'Hostname',
                                       'Auth']

    def test_generate_POST_web(self):
        request = DummyRequest([''])

        for input_type, args in [("string", copy.deepcopy(self.default_args)), (
                "bytes", {k.encode('utf-8'): [v[0].encode('utf-8')] for k, v in copy.deepcopy(self.default_args).items()})]:
            with self.subTest(input_type=input_type):
                request.args = args
                request.method = 'POST'
                result = GeneratorPage().render(request)
                self.assert_generate_result_ok(json.loads(result))

    def test_generate_POST_web_image(self):
        request = DummyRequest([''])

        for input_type in ["string", "bytes"]:
            args = copy.deepcopy(self.default_args)
            args['type'] = ["web_image"]
            args['web_image'] = [
                (
                    'web_image_test.png',
                    dataPath.child("tests").child("web_image_test.png").open('rb'),
                    'image/png'
                )
            ]

            boundary, body = encode_form(args)

            if input_type == "bytes":
                args = {k.encode('utf-8'): [v[0].encode('utf-8') if k != "web_image" else v] for k, v in args.items()}

            request.content = io.BytesIO(body)  # open("web_image_test.png", 'rb')
            request.requestHeaders = Headers(
                {'content-type': [b'multipart/form-data; boundary=' + boundary],
                 'content-length': ['26936']})

            with self.subTest(input_type=input_type):
                request.args = args

                request.method = 'POST'

                result = GeneratorPage().render(request)
                canarydrop = get_canarydrop(json.loads(result)['Token'])

                assert ImageChops.difference(
                    Image.open(dataPath.child("tests").child("web_image_test.png").path),
                    Image.open(canarydrop['web_image_path'])
                ).getbbox() is None

                self.assert_generate_result_ok(json.loads(result))

# class TestManagePage(TestCase):
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
