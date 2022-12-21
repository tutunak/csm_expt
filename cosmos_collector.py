import datetime
import os
import time
import requests
from prometheus_client import start_http_server, Gauge


class CustomExporter:
    def __init__(self, endpoint="http://localhost:26657", port=9877) -> None:
        self.endpoint = endpoint
        self.port = port
        self.metric_dict = {}

    @staticmethod
    def __time_metric(metric, block_time):
        current_time = datetime.datetime.now()
        block_time = datetime.datetime.strptime(block_time.split('.')[0], "%Y-%m-%dT%H:%M:%S")
        time_diff = current_time - block_time
        metric.set(time_diff.seconds)

    def set_metrics(self, block_header, peers):
        if self.metric_dict.get("time_diff") is None:
            self.metric_dict["time_diff"] = Gauge("time_diff", "time diff")
        self.__time_metric(self.metric_dict["time_diff"], block_header["time"])

        if self.metric_dict.get("block_height") is None:
            self.metric_dict["block_height"] = Gauge("block_height", "block_height")
        self.metric_dict["block_height"].set(int(block_header["height"]))

        if self.metric_dict.get("count_peers") is None:
            self.metric_dict["count_peers"] = Gauge("count_peers", "count_peers")
        self.metric_dict["count_peers"].set(peers)

    def set_value(self, metric_name, block_hash, block_height, value):
        self.metric_dict[metric_name].labels(block_hash, block_height).set(value)

    def get_peers(self):
        response = requests.get(f"{self.endpoint}/net_info")
        return response.json()["result"]["n_peers"]

    def get_block(self):
        response = requests.get(f"{self.endpoint}/block")
        return response.json()

    def __last_block_hash(self):
        pass

    def main(self):
        start_http_server(self.port)
        while True:
            block = self.get_block()
            peers = self.get_peers()
            self.set_metrics(block["result"]["block"]["header"], peers)
            time.sleep(1)


if __name__ == "__main__":
    exporter_port = int(os.environ.get("EXPORTER_PORT", "9877"))
    c = CustomExporter(port=exporter_port)
    c.main()
