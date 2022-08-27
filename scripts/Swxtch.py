import argparse
import datetime
import json
from threading import Thread

import requests
import urllib3
from dateutil import parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()


class DebugStatus:
    def __init__(self, *args):
        if args:
            self.host = args[0]

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

    def fetch_status(self):
        return self.__serviceStatus.fetch()

    def fetch_startTime(self):
        return self.__startTime.fetch()

    @classmethod
    def dispatch_status(cls, host):
        obj = cls(host)
        return [obj.path, "serviceStatus", obj.fetch_status()]

    @classmethod
    def dispatch_startTime(cls, host):
        obj = cls(host)
        return [obj.path, "startTime", obj.fetch_startTime()]


class DebugAgents:
    def __init__(self, *args):
        if args:
            self.host = args[0]

        self.path = "swxtch/debug/v1"
        self.method = "agents"

        self.__api = Parameters(self.host, self.path, self.method)

    def debug_agents_fetch(self):

        documents = []
        agents = self.__api.fetch()

        if agents:
            for agent in agents:

                try:

                    document = {"fields": agent, "host": self.host, "name": "debug_agent"}
                    documents.append(document)

                except Exception:
                    continue

        return documents

    def fetch(self):
        return self.__api.fetch()

    @classmethod
    def dispatch(cls, host):
        obj = cls(host)
        return [obj.path, obj.method, obj.fetch()]


class SwitchLinks:
    def __init__(self, *args):
        if args:
            self.host = args[0]

        self.path = "swxtch/mesh/v1/tool"
        self.method = "listSwitchLinks"
        self.__api = Parameters(self.host, self.path, self.method)

    def switch_links_fetch(self):

        documents = []
        meshes = self.__api.fetch()

        if meshes and isinstance(meshes, list):
            for mesh in meshes:

                if mesh["switchLinksList"] and isinstance(mesh["switchLinksList"], list):
                    for link in mesh["switchLinksList"]:

                        try:

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
                            continue

        return documents

    def fetch(self):
        return self.__api.fetch()

    @classmethod
    def dispatch(cls, host):
        obj = cls(host)
        return [obj.path, obj.method, obj.fetch()]


class SwitchRouteTable:
    def __init__(self, *args):
        if args:
            self.host = args[0]

        self.path = "swxtch/mesh/v1/tool"
        self.method = "listSwitchRouteTable"
        self.__api = Parameters(self.host, self.path, self.method)

    def switch_route_table_fetch(self):

        documents = []
        meshes = self.__api.fetch()

        if meshes and isinstance(meshes, list):
            for mesh in meshes:

                if mesh["switchRouteList"] and isinstance(mesh["switchRouteList"], list):
                    for route in mesh["switchRouteList"]:

                        try:

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

                        except Exception:
                            continue

        return documents

    def fetch(self):
        return self.__api.fetch()

    @classmethod
    def dispatch(cls, host):
        obj = cls(host)
        return [obj.path, obj.method, obj.fetch()]


class SwitchAgentSubscriptions:
    def __init__(self, *args):
        if args:
            self.host = args[0]

        self.path = "swxtch/mesh/v1/tool"
        self.method = "listAgentSubscription"
        self.__api = Parameters(self.host, self.path, self.method)

    def switch_agent_subs_fetch(self):

        documents = []
        subs = self.__api.fetch()

        if subs and isinstance(subs, list):
            for sub in subs:

                try:

                    fields = {
                        "s_mcastgroupip": sub["mcastGroupIp"],
                        "as_subagents": [
                            "{}:{}".format(k, v)
                            for k, v in sub["subscribedAgents"].items()
                        ],
                    }

                    document = {
                        "fields": fields,
                        "host": self.host,
                        "name": "switch_agent_sub",
                    }

                    documents.append(document)

                except Exception:
                    continue

        return documents

    def fetch(self):
        return self.__api.fetch()

    @classmethod
    def dispatch(cls, host):
        obj = cls(host)
        return [obj.path, obj.method, obj.fetch()]


class SwitchSubscriptions:
    def __init__(self, *args):
        if args:
            self.host = args[0]

        self.path = "swxtch/mesh/v1/tool"
        self.method = "listSwitchSubscription"
        self.__api = Parameters(self.host, self.path, self.method)

    def switch_subscriptions_fetch(self):

        documents = []
        meshes = self.__api.fetch()

        if meshes and isinstance(meshes, list):
            for mesh in meshes:

                if mesh["mcastGroupSwitchData"] and isinstance(
                    mesh["mcastGroupSwitchData"], list
                ):

                    for sub in mesh["mcastGroupSwitchData"]:

                        try:

                            fields = {
                                "s_meshname": mesh["meshName"],
                                "s_mcastgroupip": sub["mcastGroupIp"],
                                "as_subswitchmap": [
                                    "{}:{}".format(k, v)
                                    for k, v in sub["subscribedSwitchMap"].items()
                                ],
                            }

                            document = {
                                "fields": fields,
                                "host": self.host,
                                "name": "switch_sub",
                            }

                            documents.append(document)

                        except Exception:
                            pass

        return documents

    def fetch(self):
        return self.__api.fetch()

    @classmethod
    def dispatch(cls, host):
        obj = cls(host)
        return [obj.path, obj.method, obj.fetch()]


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


class Swxtch(
    DebugStatus,
    DebugAgents,
    SwitchLinks,
    SwitchRouteTable,
    SwitchAgentSubscriptions,
    SwitchSubscriptions,
):
    def __init__(self, host, *args):
        self.host = host

        if args:
            (self.magnum,) = args

        DebugStatus.__init__(self)
        DebugAgents.__init__(self)
        SwitchLinks.__init__(self)
        SwitchRouteTable.__init__(self)
        SwitchAgentSubscriptions.__init__(self)
        SwitchSubscriptions.__init__(self)

        self.exec_list = [
            self.debug_status_fetch,
            self.debug_agents_fetch,
            self.switch_links_fetch,
            self.switch_route_table_fetch,
            self.switch_agent_subs_fetch,
            self.switch_subscriptions_fetch,
        ]

        self.documents = []

    @classmethod
    def magnum_annotate(cls, host, magnum):
        # Create magnum obj
        return cls(host, magnum)

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
    args_parser = argparse.ArgumentParser(description="Swxtch API Poller Program")

    args_parser.add_argument(
        "-host",
        "--swxtch-host",
        required=False,
        type=str,
        metavar="<ip>",
        default="localhost:3000",
        help="Swxtch IP Address (default localhost:3000)",
    )

    sub = args_parser.add_subparsers(dest="which")
    sub.required = False

    sub_magnum = sub.add_parser("magnum", help="Use Magnum Annotations")
    sub_magnum.set_defaults(which="magnum")

    sub_magnum.add_argument(
        "-cluster",
        "--cluster-address",
        required=True,
        type=str,
        metavar="<ip>",
        help="Magnum Cluster IP Address",
    )

    sub_magnum.add_argument(
        "-host",
        "--swxtch-host",
        required=False,
        type=str,
        metavar="<ip>",
        default="localhost:3000",
        help="Swxtch IP Address (default localhost:3000)",
    )

    sub_export = sub.add_parser("export", help="Generate JSON Server Files")
    sub_export.set_defaults(which="export")

    sub_export.add_argument(
        "-host",
        "--swxtch-host",
        required=False,
        type=str,
        metavar="<ip>",
        default="localhost:3000",
        help="Swxtch IP Address (default localhost:3000)",
    )

    args = args_parser.parse_args()

    if args.which == "export":

        dispatch_funcs = [
            DebugStatus.dispatch_startTime,
            DebugStatus.dispatch_status,
            DebugAgents.dispatch,
            SwitchLinks.dispatch,
            SwitchRouteTable.dispatch,
            SwitchAgentSubscriptions.dispatch,
            SwitchSubscriptions.dispatch,
        ]

        db = {}
        routes = {}

        for func in dispatch_funcs:
            path, method, data = func(args.swxtch_host)

            db.update({method: data})
            routes["/{}/{}".format(path, method)] = method

        with open("db.json", "w") as outfile:
            json.dump(db, outfile, indent=4)

        with open("routes.json", "w") as outfile:
            json.dump(routes, outfile, indent=4)

        quit()

    if args.which == "magnum":
        print("Not yet implemented")
        quit()

    swxtch = Swxtch(host=args.swxtch_host)

    print(json.dumps(swxtch.collect, indent=1))


if __name__ == "__main__":
    main()
