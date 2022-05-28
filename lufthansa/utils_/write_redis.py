from mitmproxy import ctx
from mitmproxy.http import HTTPFlow
import re
from feapder.db.redisdb import RedisDB
import json


class RequestModify:
    def process_item(self, datas, key):
        save_request = RedisDB(ip_ports="localhost:6379", db=0)
        datas = json.dumps(datas)
        save_request.hset(table='lufthansa', key=key, value=datas)

    def requestheaders(self, flow: HTTPFlow):
        url = flow.request.url
        complete = r'^https://.*/rs/.+?execution=.+3&l=en$'
        if re.search(complete, url):
            # ctx.log.info(f">>>>>>>>>>>{url}<<<<<<<<<<<<<")
            headers = dict(flow.request.headers)
            request_body = {'url': url, 'headers': headers}
            ctx.log.info(f"{request_body}")
            self.process_item(datas=request_body, key='one')


addons = [
    RequestModify()
]