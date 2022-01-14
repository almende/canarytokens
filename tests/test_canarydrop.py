import tests.config
from canarydrop import Canarydrop
# from redismanager import db
import settings
import re

settings.DOMAINS = ['localhost']
import setup_db

class TestGenerateCanaryToken:
    def test_make_canarytoken_with_email(self, monkeypatch):
        token_type = 'web'
        alert_email_enabled = True
        email = 'a@b.com'
        alert_webhook_enabled = False
        webhook = ''
        canarytoken = 'b99c88am5hfa6txclsqitk06v'
        memo = 'temp'
        browser_scanner = False

        canarydrop = Canarydrop(
            type=token_type,
            generate=True,
            alert_email_enabled=alert_email_enabled,
            alert_email_recipient=email,
            alert_webhook_enabled=alert_webhook_enabled,
            alert_webhook_url=webhook,
            canarytoken=canarytoken,
            memo=memo,
            browser_scanner_enabled=browser_scanner)

        assert canarydrop._drop['type'] == token_type
        assert re.match("^http://localhost/.*/{}/.*$".format(canarydrop.canarytoken.value()), canarydrop.get_url())
        assert canarydrop.get_requested_output_channels() == ['Email']
        assert canarydrop._drop['alert_webhook_url'] == webhook
        assert canarydrop.canarytoken.value() == canarytoken
        assert canarydrop._drop['memo'] == memo
        assert canarydrop._drop['browser_scanner_enabled'] == browser_scanner

    def test_make_canarytoken_with_email_and_webhook(self, monkeypatch):
        token_type = 'web'
        alert_email_enabled = True
        email = 'a@b.com'
        alert_webhook_enabled = True
        webhook = 'localhost:5000/webhook'
        canarytoken = 'b99c88am5hfa6txclsqitk06v'
        memo = 'temp'
        browser_scanner = False

        canarydrop = Canarydrop(
            type=token_type,
            generate=True,
            alert_email_enabled=alert_email_enabled,
            alert_email_recipient=email,
            alert_webhook_enabled=alert_webhook_enabled,
            alert_webhook_url=webhook,
            canarytoken=canarytoken,
            memo=memo,
            browser_scanner_enabled=browser_scanner)

        assert canarydrop._drop['type'] == token_type
        assert re.match("^http://localhost/.*/{}/.*$".format(canarydrop.canarytoken.value()), canarydrop.get_url())
        assert canarydrop.get_requested_output_channels() == ['Email', 'Webhook']
        assert canarydrop._drop['alert_webhook_url'] == webhook
        assert canarydrop.canarytoken.value() == canarytoken
        assert canarydrop._drop['memo'] == memo
        assert canarydrop._drop['browser_scanner_enabled'] == browser_scanner

    def test_make_canarytoken_with_webhook(self, monkeypatch):
        token_type = 'web'
        alert_email_enabled = False
        email = ''
        alert_webhook_enabled = True
        webhook = 'localhost:5000/webhook'
        canarytoken = 'b99c88am5hfa6txclsqitk06v'
        memo = 'temp'
        browser_scanner = False

        canarydrop = Canarydrop(
            type=token_type,
            generate=True,
            alert_email_enabled=alert_email_enabled,
            alert_email_recipient=email,
            alert_webhook_enabled=alert_webhook_enabled,
            alert_webhook_url=webhook,
            canarytoken=canarytoken,
            memo=memo,
            browser_scanner_enabled=browser_scanner)

        assert canarydrop._drop['type'] == token_type
        assert re.match("^http://localhost/.*/{}/.*$".format(canarydrop.canarytoken.value()), canarydrop.get_url())
        assert canarydrop.get_requested_output_channels() == ['Webhook']
        assert canarydrop._drop['alert_webhook_url'] == webhook
        assert canarydrop.canarytoken.value() == canarytoken
        assert canarydrop._drop['memo'] == memo
        assert canarydrop._drop['browser_scanner_enabled'] == browser_scanner
