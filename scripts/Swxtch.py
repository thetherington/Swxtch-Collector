import argparse
import datetime
import json
from threading import Thread

import requests
import urllib3
from dateutil import parser

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings()


class Base:
    def __init__(self, host, path, method):
        self.host = host
        self.path = path
        self.method = method
        self.headers = {"content-type": "application/json"}
        self.url = "http://{}/{}/{}".format(self.host, self.path, self.method)
        self.store = {}

    def fetch(self, url=None):

        try:

            url = url or self.url

            resp = requests.get(url, verify=False, timeout=10)
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

    def get(self, key):
        return self.store.get(key, {})

    @classmethod
    def dispatch(cls, host):
        obj = cls(host=host)  # pylint: disable=no-value-for-parameter
        return [obj.path, obj.method, obj.fetch()]


class DebugStatus(Base):
    def __init__(self, host):
        super().__init__(host=host, path="swxtch/debug/v1", method="serviceStatus")

        self.method_start_time = "startTime"

        self.url_start_time = "http://{}/{}/{}".format(
            self.host, self.path, self.method_start_time
        )

    def collect(self, **context):  # pylint: disable=unused-argument

        fields = {}

        start_time = self.fetch(self.url_start_time)

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

        service_status = self.fetch()

        if service_status:

            try:
                fields.update({"s_status": service_status["status"]})
            except Exception:
                pass

        if len(fields.keys()) == 0:
            return []

        document = {"fields": fields, "host": self.host, "name": "debug_status"}

        return [document]

    @classmethod
    def dispatch_start_time(cls, host):
        obj = cls(host)
        return [obj.path, "startTime", obj.fetch(obj.url_start_time)]


class DebugAgents(Base):
    def __init__(self, host):
        super().__init__(host=host, path="swxtch/debug/v1", method="agents")

    def collect(self, **context):  # pylint: disable=unused-argument

        documents = []
        agents = self.fetch()

        # annotations = context.get("annotations") or []

        if agents:
            for agent in agents:

                try:

                    document = {"fields": agent, "host": self.host, "name": "debug_agent"}
                    documents.append(document)

                    self.store.update({agent["name"]: agent})

                except Exception:
                    continue

        return documents


class SwitchLinks(Base):
    def __init__(self, host):
        super().__init__(host=host, path="swxtch/mesh/v1/tool", method="listSwitchLinks")

    def collect(self, **context):  # pylint: disable=unused-argument

        documents = []
        meshes = self.fetch()

        # annotations = context.get("annotations") or []

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


class SwitchRouteTable(Base):
    def __init__(self, host):
        super().__init__(
            host=host, path="swxtch/mesh/v1/tool", method="listSwitchRouteTable"
        )

    def collect(self, **context):  # pylint: disable=unused-argument

        documents = []
        meshes = self.fetch()

        # annotations = context.get("annotations") or []

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


class SwitchAgentSubscriptions(Base):
    def __init__(self, host):
        super().__init__(
            host=host, path="swxtch/mesh/v1/tool", method="listAgentSubscription"
        )

    def collect(self, **context):  # pylint: disable=unused-argument

        documents = []
        subs = self.fetch()

        # annotations = context.get("annotations") or []

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


class SwitchSubscriptions(Base):
    def __init__(self, host):
        super().__init__(
            host=host, path="swxtch/mesh/v1/tool", method="listSwitchSubscription"
        )

    def collect(self, **context):  # pylint: disable=unused-argument

        documents = []
        meshes = self.fetch()

        # agents = context.get("agents") or []

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


class Swxtch:
    def __init__(self, host, *args):
        self.host = host

        if args:
            (self.magnum,) = args

        self.debug_status = DebugStatus(host=self.host)
        self.debug_agents = DebugAgents(host=self.host)
        self.switch_links = SwitchLinks(host=self.host)
        self.switch_route_table = SwitchRouteTable(host=self.host)
        self.agent_subscriptions = SwitchAgentSubscriptions(host=self.host)
        self.switch_suscriptions = SwitchSubscriptions(host=self.host)

        self.exec_list = [
            self.debug_status.collect,
            self.debug_agents.collect,
            self.switch_links.collect,
            self.switch_route_table.collect,
            self.agent_subscriptions.collect,
            self.switch_suscriptions.collect,
        ]

        self.context = {
            "agents": self.debug_agents.get,
            "links": self.switch_links.get,
            "routes": self.switch_route_table.get,
            "magnum": None,
        }

        self.documents = []

    @classmethod
    def magnum_annotate(cls, host, magnum):
        # Create magnum obj
        return cls(host, magnum)

    def store(self, func, **context):
        self.documents.extend(func(**context))

    @property
    def collect(self):
        self.documents = []

        threads = [
            Thread(target=self.store, args=(func,), kwargs=self.context)
            for func in self.exec_list
        ]

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
            DebugStatus.dispatch,
            DebugStatus.dispatch_start_time,
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

    data = swxtch.collect
    print(json.dumps(data, indent=1))
    print(len(data))


if __name__ == "__main__":
    main()
