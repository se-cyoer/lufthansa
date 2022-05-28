from lufthansa.lufthansa.db.redisdb import RedisDB
from mitmproxy import ctx
from mitmproxy.http import HTTPFlow
import re


def read_request():
    redisdb=RedisDB(ip_ports="localhost:6379", db=0)
    datas = redisdb.zget('Lufthansa', is_pop=False, count=-1)

    for data in datas:
        print(data)

read_request()


# class RequestModify:
#     def requestheaders(self, flow: HTTPFlow):
#
#                 headers = req.get('headers')
#                 url = req.get('url')
#                 if re.search(r'^https://.*/rs/.+?execution=.+3&l=en$', url):
#                     flow.request.headers['user-agent'] = str(headers.get('user-agent'))
#                     flow.request.headers['referer'] = str(headers.get('referer'))
#                     flow.request.headers['cookie'] = str(headers.get('cookie'))
#                     flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
#                     flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
#                     flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
#                     flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
#                     flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
#                     flow.request.headers['accept-encoding'] = str(headers.get('accept-encoding'))
#                     flow.request.headers['accept-language'] = str(headers.get('accept-language'))
#                     ctx.log.info(flow.request.headers)
#
#                 elif re.search(r'^https://.*/rs/.+?execution=.+2&l=en$', url):
#                     flow.request.headers['user-agent'] = str(headers.get('user-agent'))
#                     flow.request.headers['cookie'] = str(headers.get('cookie'))
#                     flow.request.headers['cache-control'] = str(headers.get('cache-control'))
#                     flow.request.headers['referer'] = str(headers.get('referer'))
#                     flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
#                     flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
#                     flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
#                     flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
#                     flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
#                     ctx.log.info(flow.request.headers)
#
#                 else:
#                     flow.request.headers['user-agent'] = str(headers.get('user-agent'))
#                     flow.request.headers['cookie'] = str(headers.get('cookie'))
#                     flow.request.headers['cache-control'] = str(headers.get('cache-control'))
#                     flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
#                     flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
#                     flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
#                     flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
#                     flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
#                     ctx.log.info(flow.request.headers)
#
#
# addons = [
#     RequestModify()
# ]
