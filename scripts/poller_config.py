import json

from Swxtch import Swxtch
from insite_plugin import InsitePlugin


class Plugin(InsitePlugin):
    def can_group(self):
        return False

    def fetch(self, hosts):

        try:

            self.collector

        except Exception:

            self.collector = Swxtch(hosts[-1])

        return json.dumps(self.collector.collect)
