import tests.config
import setup_db
from twisted.trial.unittest import TestCase
from twisted.web.test.test_web import DummyRequest
import json

from switchboard import Switchboard
import settings
from channel_http import CanarytokenPage, ChannelHTTP
from httpd_site import GeneratorPage
from twisted.python import log as l
from queries import get_canarydrop

settings.DOMAINS = ['localhost']

switchboard = Switchboard()
canarytokens_httpd = ChannelHTTP(port=settings.CHANNEL_HTTP_PORT,
                                 switchboard=switchboard)


class TestTriggerWebBug(TestCase):
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

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        self.observer = l.PythonLoggingObserver()

    def test_trigger_GET_no_valid_token(self):
        request = DummyRequest([''])
        request.path = b"/articles/images/about/sfnhvgfvslfhkuym7nva2si2z/contact.php"
        request.args = {}
        request.method = 'GET'

        self.observer.start()

        with self.assertLogs("twisted") as cm:
            result = CanarytokenPage().render(request)

        assert 'WARNING:twisted:Error in render GET: No Canarytoken present' in cm.output
        assert result == CanarytokenPage.GIF.encode('utf-8')

        self.observer.stop()

    def test_trigger_GET_valid_token(self):
        # Make a token using /generate
        request = DummyRequest([''])
        request.args = self.default_args
        request.method = 'POST'
        result_token = json.loads(GeneratorPage().render(request))
        canarydrop_before = get_canarydrop(result_token['Token'])

        # instantiate CanaryTokenPage
        switchboard = Switchboard()
        canarytoken_page = CanarytokenPage()
        canarytoken_page.init(switchboard=switchboard)

        # trigger token
        request = DummyRequest([''])
        request.path = "/articles/images/about/{}/contact.php".format(result_token["Token"]).encode('utf-8')
        request.args = {}
        request.method = 'GET'

        result = canarytoken_page.render(request)
        assert result == CanarytokenPage.GIF.encode('utf-8')

        # get token from db
        canarydrop_after = get_canarydrop(result_token['Token'])

        triggered_list = canarydrop_after['triggered_list']
        del canarydrop_after['triggered_list']

        assert len(triggered_list) == 1
        assert list(triggered_list.values())[0]['input_channel'] == 'HTTP'
        assert canarydrop_before == canarydrop_after
