import copy
import datetime
import json
from threading import Thread

import requests
import urllib3
from dateutil import parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()


class DebugStatus:
    def __init__(self):
        self.path = "swxtch/debug/v1"
        self.__startTime = Parameters(self.host, self.path, "startTime")
        self.__serviceStatus = Parameters(self.host, self.path, "serviceStatus")

    def debug_status_fetch(self):

        fields = {}

        start_time = self.__startTime.fetch()

        if start_time:

            try:
                date_delta = datetime.datetime.utcnow() - parser.parse(
                    start_time["startTime"]
                ).replace(tzinfo=None)

                days = date_delta.days
                hours, remainder = divmod(date_delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                fields.update(
                    {
                        "t_startTime": start_time["startTime"],
                        "i_days": days,
                        "i_hours": hours,
                        "i_minutes": minutes,
                    }
                )

            except Exception:
                fields.update({"t_startTime": start_time["startTime"]})

        service_status = self.__serviceStatus.fetch()

        if service_status:

            try:
                fields.update({"s_status": service_status["status"]})
            except Exception:
                pass

        if len(fields.keys()) == 0:
            return []

        document = {"fields": fields, "host": self.host, "name": "debug_status"}

        return [document]


class DebugAgents:
    def __init__(self):
        self.path = "swxtch/debug/v1"
        self.__agents = Parameters(self.host, self.path, "agents")

    def debug_agents_fetch(self):

        documents = []
        agents = self.__agents.fetch()

        if agents:

            try:

                for agent in agents:
                    document = {"fields": agent, "host": self.host, "name": "debug_agent"}
                    documents.append(document)

            except Exception:
                pass

        return documents


class SwitchLinks:
    def __init__(self):
        self.path = "swxtch/mesh/v1/tool"
        self.__links = Parameters(self.host, self.path, "listSwitchLinks")

    def switch_links_fetch(self):

        documents = []
        meshes = self.__links.fetch()

        if meshes and isinstance(meshes, list):
            for mesh in meshes:

                try:

                    if mesh["switchLinksList"] and isinstance(
                        mesh["switchLinksList"], list
                    ):
                        for link in mesh["switchLinksList"]:

                            fields = {
                                "s_meshname": mesh["meshName"],
                                "s_switch": link["switch"],
                                "as_switchlinks": link["switchLinks"],
                            }

                            document = {
                                "fields": fields,
                                "host": self.host,
                                "name": "switch_links",
                            }

                            documents.append(document)

                except Exception:
                    pass

        return documents


class SwitchRouteTable:
    def __init__(self):
        self.path = "swxtch/mesh/v1/tool"
        self.__routeTable = Parameters(self.host, self.path, "listSwitchRouteTable")

    def switch_route_table_fetch(self):

        documents = []
        meshes = self.__routeTable.fetch()

        if meshes and isinstance(meshes, list):
            for mesh in meshes:

                if mesh["switchRouteList"] and isinstance(mesh["switchRouteList"], list):
                    for route in mesh["switchRouteList"]:

                        fields = {
                            "s_meshname": mesh["meshName"],
                            "s_switchdst": route["switchDst"],
                            "as_switchLinks": route["switchLinks"],
                        }

                        document = {
                            "fields": fields,
                            "host": self.host,
                            "name": "switch_route_table",
                        }

                        documents.append(document)

        return documents


class Parameters:
    def __init__(self, host, path, method):
        self.headers = {"content-type": "application/json"}

        self.host = host
        self.path = path
        self.method = method

        self.url = "http://{}/{}/{}".format(self.host, self.path, self.method)

    def fetch(self):

        try:
            resp = requests.get(self.url, verify=False, timeout=10)

            resp.close()

            data = json.loads(resp.text)

            return data

        except Exception as error:
            with open(self.host, "a+") as log:
                log.write(
                    str(datetime.datetime.now())
                    + " --- "
                    + self.method
                    + "\t"
                    + str(error)
                    + "\r\n"
                )

            return None


class Swxtch(DebugStatus, DebugAgents, SwitchLinks, SwitchRouteTable):
    def __init__(self, host, *args):
        self.host = host

        if args:
            (self.magnum_cluster,) = args

        DebugStatus.__init__(self)
        DebugAgents.__init__(self)
        SwitchLinks.__init__(self)
        SwitchRouteTable.__init__(self)

        self.exec_list = [
            self.debug_status_fetch,
            self.debug_agents_fetch,
            self.switch_links_fetch,
            self.switch_route_table_fetch,
        ]

        self.documents = []

    @classmethod
    def magnum_annotate(cls, host, cluster_ip):
        # Create magnum obj
        return cls(host, cluster_ip)

    def store(self, func):
        self.documents.extend(func())

    @property
    def collect(self):
        self.documents = []

        threads = [Thread(target=self.store, args=(func,)) for func in self.exec_list]

        for x in threads:
            x.start()

        for y in threads:
            y.join()

        return self.documents


def main():
    swxtch = Swxtch(host="localhost:3000")

    print(json.dumps(swxtch.collect, indent=1))


if __name__ == "__main__":
    main()
