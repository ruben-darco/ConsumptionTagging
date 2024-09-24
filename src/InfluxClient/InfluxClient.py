from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxClient():
    def __init__(self, url :str, bucket :str, org : str, token : str): 
        self.token = token
        self.url = url
        self.org = org
        self.bucket = bucket
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        
    def write(self, p : str):

        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=self.bucket, org=self.org, record=p, time_precision="s")
        write_api.close()

    def close(self):
        self.client.close()
    