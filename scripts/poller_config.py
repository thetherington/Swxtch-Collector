import json

from Swxtch import Swxtch
from insite_plugin import InsitePlugin


class Plugin(InsitePlugin):
    def can_group(self):
        return False

    def fetch(self, hosts):

        magnum = None

        try:

            self.collector

        except Exception:

            if magnum:
                self.collector = Swxtch.magnum(hosts[-1], magnum)

            else:
                self.collector = Swxtch(hosts[-1])

        return json.dumps(self.collector.collect)
