from models import InfluxClient
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
import logging
import json
import jsonschema
 
g_client : InfluxClient

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # suppress all standard logging.
    def log_message(self, format, *args):
        return

    def d_GET(self): 
        logging.debug("%s %s", self.client_address[0], self.requestline)
        self.send_response(200)
        self.end_headers()

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
               
                g_client.write(p)
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
       
        # g_client = InfluxClient(url= "https://influx.prof-x.net", bucket="Nintex", org="Prof-X", token="aWz3qJTgkjBe47XEFgCeNJ1ZJdMxW0c3TEVSSKW4qb-ZvFB97CgI4NqfdNzFwhLqf_4qgtxAcZlA82LHAHG-zA=="
        g_client = InfluxClient(url= "https://influx.prof-x.net", bucket="Nintex", org="Prof-X", token="aWz3qJTgkjBe47XEFgCeNJ1ZJdMxW0c3TEVSSKW4qb-ZvFB97CgI4NqfdNzFwhLqf_4qgtxAcZlA82LHAHG-zA==")  
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("^C received, shutting down server")
        g_client.close();
        httpd.socket.close()

if __name__ == '__main__':
    main()