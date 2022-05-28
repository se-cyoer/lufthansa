from mitmproxy import ctx
from mitmproxy.http import HTTPFlow
import re
import json
from random import choice


class RequestModify:
    def requestheaders(self, flow: HTTPFlow):
        ua_list = ['Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
                   'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
                   ]
        with open('lufthansa_re.json') as fp:
            request_body = fp.readlines()
            for request in request_body:
                req = json.loads(request)
                headers = req.get('headers')
                url = req.get('url')
                if re.search(r'^https://.*/rs/.+?execution=.+3&l=en$', url):
                    # str(headers.get('user-agent'))
                    flow.request.headers['user-agent'] = choice(ua_list)
                    flow.request.headers['referer'] = str(headers.get('referer'))
                    flow.request.headers['cookie'] = str(headers.get('cookie'))
                    flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
                    flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
                    flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
                    flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
                    flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
                    flow.request.headers['accept-encoding'] = str(headers.get('accept-encoding'))
                    flow.request.headers['accept-language'] = str(headers.get('accept-language'))
                    ctx.log.info(flow.request.headers)
                #
                # elif re.search(r'^https://.*/rs/.+?execution=.+2&l=en$', url):
                #     flow.request.headers['user-agent'] = str(headers.get('user-agent'))
                #     flow.request.headers['cookie'] = str(headers.get('cookie'))
                #     flow.request.headers['cache-control'] = str(headers.get('cache-control'))
                #     flow.request.headers['referer'] = str(headers.get('referer'))
                #     flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
                #     flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
                #     flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
                #     flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
                #     flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
                #     ctx.log.info(flow.request.headers)
                #
                # else:
                #     flow.request.headers['user-agent'] = str(headers.get('user-agent'))
                #     flow.request.headers['cookie'] = str(headers.get('cookie'))
                #     flow.request.headers['cache-control'] = str(headers.get('cache-control'))
                #     flow.request.headers['sec-fetch-site'] = str(headers.get('sec-fetch-site'))
                #     flow.request.headers['sec-fetch-mode'] = str(headers.get('sec-fetch-mode'))
                #     flow.request.headers['sec-fetch-user'] = str(headers.get('sec-fetch-user'))
                #     flow.request.headers['sec-fetch-dest'] = str(headers.get('sec-fetch-dest'))
                #     flow.request.headers['upgrade-insecure-requests'] = str(headers.get('upgrade-insecure-requests'))
                #     ctx.log.info(flow.request.headers)


addons = [
    RequestModify()
]
