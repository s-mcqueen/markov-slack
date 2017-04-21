'''Slack client wrapper'''

from slackclient import SlackClient

class Client(object):

    def __init__(self, api_key, channel, username, icon_url=None):
        self.slack = SlackClient(api_key)
        self.channel = channel
        self.username = username
        self.icon_url = icon_url

    def post(self, message):
        self.slack.api_call(
            'chat.postMessage',
            channel=self.channel,
            username=self.username,
            icon_url=self.icon_url,
            text=message)
