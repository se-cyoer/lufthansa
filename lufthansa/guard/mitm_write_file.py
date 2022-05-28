from mitmproxy import ctx
from mitmproxy.http import HTTPFlow
import json
import re


class RequestFilter:
    def requestheaders(self, flow: HTTPFlow):
        url = flow.request.url
        if re.search(r'^https://.*/rs/.+?execution=.+4&l=en$', url):
            ctx.log.info(f">>>>>>>>>>>{url}<<<<<<<<<<<<<")
            headers = dict(flow.request.headers)
            request_body = {'url': url, 'headers': headers}
            ctx.log.info(f"{request_body}")
            with open('lufthansa_re.json', 'w') as fp:
                fp.write(json.dumps(request_body))
                fp.close()
        if re.search(r'^https://.*/rs/.+?execution=.+3&l=en$', url):
            ctx.log.info(f">>>>>>>>>>>{url}<<<<<<<<<<<<<")
            headers = dict(flow.request.headers)
            request_body = {'url': url, 'headers': headers}
            ctx.log.info(f"{request_body}")
            with open('lufthansa_re.json', 'w') as fp:
                fp.write(json.dumps(request_body))
                fp.close()


addons = [
    RequestFilter()
]

# import time
# from mitmproxy import ctx
# from mitmproxy.http import HTTPFlow
# import re
# from feapder.db.redisdb import RedisDB
#
#
# class RequestModify:
#     def process_item(self, datas):
#         save_request = RedisDB(ip_ports="localhost:6379", db=0)
#         timestamp = time.time()
#         save_request.zadd(table='c', values=datas, prioritys=timestamp)
#
#     def requestheaders(self, flow: HTTPFlow):
#         url = str(flow.request.url)
#         # complete = r'(^https://.*/rs/.+?execution=.+1&l=en$)|(^https://.*/rs/.+?execution=.+2&l=en$)|(^https://.*/rs/.+?execution=.+3&l=en$)'
#         complete = r'^https://.*/rs/.+?execution=.+3&l=en$'
#         if re.search(complete, url):
#             ctx.log.info(f">>>>>>>>>>>{url}<<<<<<<<<<<<<")
#             headers = dict(flow.request.headers)
#             request_body = {'url': url, 'headers': headers}
#             ctx.log.info(f"{request_body}")
#             self.process_item(request_body)
#
#
# addons = [
#     RequestModify()
# ]