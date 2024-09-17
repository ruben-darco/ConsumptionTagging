from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
import logging
import json
import time
import os
import jsonschema
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

g_influx_bucket = "Nintex"
g_influx_org = "Prof-X"

client = InfluxDBClient(url="https://influx.prof-x.net", token="aWz3qJTgkjBe47XEFgCeNJ1ZJdMxW0c3TEVSSKW4qb-ZvFB97CgI4NqfdNzFwhLqf_4qgtxAcZlA82LHAHG-zA==", org=g_influx_org)





class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # supress all standard logging.
    def log_message(self, format, *args):
        return

    def do_POST(self):
        logging.debug("%s %s", self.client_address[0], self.requestline)
        for header in self.headers:
            logging.info("HEADER %s:%s", header, self.headers[header])
        logging.info("----------------------")
        
        schema ="";
        with open("schema_post.json", "r") as f:
            schema = json.load(f)
        
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            bodydata = json.loads(body)
            print(body)
            jsonschema.validate(bodydata, schema)
        except Exception as e:
            self.send_error(500, f"Failed to parse json: {e}")
            self.end_headers()
            return
        
        try:
            for usage in bodydata["usages"]:
                
                p = Point(usage["entitlementId"])
                p = p.tag("TenantId", usage["tenantId"])
                p = p.tag("EntitlementId", usage["entitlementId"])
                
                if "tags" in usage:
                    for tag in usage["tags"]:
                        p = p.tag(tag["name"], tag["value"])
                        logging.info(f"Adding tag {tag['name']} with value {tag['value']}")
                else:
                    logging.info("No extra tags provided")
                
                dt = datetime.now()
                try:
                    dt = datetime.fromisoformat(usage["timestampUtc"].replace("Z", "+00:00"))
                except Exception as e:
                    logging.debug(f"YOLA - datetime parse fail: {e}")
                    
                p = p.time(dt)
                p = p.field("usage", usage["usage"])
                print("Writing...")
                print(p)
                write_api = client.write_api(write_options=SYNCHRONOUS)
                write_api.write(bucket=g_influx_bucket, org=g_influx_org, record=p, time_precision="s")
                write_api.close()
        except Exception as e:
            self.send_error(500, f"Failed to write to influx: {e}")
            self.end_headers()
            return

        
        
        self.send_response(200)
        self.end_headers()


def main():
    logging.basicConfig(
        encoding='utf-8',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)8s %(module)s (%(funcName)s): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        )
    try:
        httpd = HTTPServer(('0.0.0.0', 8888), SimpleHTTPRequestHandler)
        logging.info("Started http-server on port 8888...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("^C received, shutting down server")
        write_api.close()
        httpd.socket.close()

if __name__ == '__main__':
    main()