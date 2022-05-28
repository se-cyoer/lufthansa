from playwright.async_api import async_playwright
from fake_useragent import FakeUserAgent
import random
import requests
import asyncio
from loguru import logger


class BasePorxy(object):
    def __init__(self, url, proxies, playwright):
        self.url = url
        self.proxies = proxies
        self.playwright = playwright
        self.fku = FakeUserAgent()

    def random_ua(self):
        """
        随机获取请求头中的user-agent字段
        :return:
        """
        return random.choice(self.fku.data_browsers.get('chrome'))

    def format_proxies(self):
        """
        格式化代理
        :return:
        """
        return [f"http://{self.proxies}", f"https://{self.proxies}", f"socks5://{self.proxies}"]

    def check_proxy(self):
        """
        检查代理是否正常
        :return:
        """
        for proxies in self.format_proxies():
            proxy = None
            if proxies.split(':')[0].startswith('http'):
                proxy = {proxies.split(':')[0]: proxies}
            else:
                proxy = {'http': proxies, 'https': proxies}
            headers = {'User-Agent': self.random_ua()}
            result = requests.get(url="http://www.baidu.com", proxies=proxy, headers=headers)
            if result.status_code == 200:
                return True
            else:
                return False


    def get(self):
        pass


class PlaywrightProxy(BasePorxy):
    try:
        async def get(self):
            """
            创建异步请求
            :return:
            """
            browser = await self.playwright.chromium.launch(headless=False, proxy={
                'server': self.format_proxies()
            })
            new_context = await browser.new_context()
            page = await new_context.new_page()
            await page.goto(self.url)
            await asyncio.sleep(10)
            return page.content()

    except Exception as e:
        logger.debug(f"Error {e}!")


async def main():
    url = "https://v.qq.com"
    proxies = "127.0.0.1:8080"
    async with async_playwright() as playwright:
        playwright_proxy = PlaywrightProxy(url=url, proxies=proxies, playwright=playwright)
        await playwright_proxy.get()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())


