# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from playwright.async_api import async_playwright
import asyncio
from scrapy.http import HtmlResponse
import re
import time


class LufthansaSpiderMiddleware:

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):

        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FormatDate:
    def __init__(self, datetimer):
        self.datetimer = datetimer
        self.localtimer = time.strftime('%Y-%m-%d', time.localtime())

    def n_m_d(self, localtimer):
        local_timer = localtimer.split('-')
        return local_timer[0], local_timer[1], local_timer[2]

    def is_date(self):
        datetimer = self.n_m_d(self.datetimer)
        local_timer = self.n_m_d(self.localtimer)
        if datetimer == local_timer:
            return None
        else:
            click_count = 0
            i_year = int(datetimer[0])
            i_month = int(datetimer[1])
            i_day = int(datetimer[2])

            l_year = int(local_timer[0])
            l_month = int(local_timer[1])

            if i_year == l_year and i_month > l_month:
                click_count = i_month - l_month
            elif i_year > l_year and i_month == l_month:
                click_count = (i_year - l_year) * 12
            elif i_year > l_year and i_month > l_month:
                year = i_year - l_year
                month = i_month - l_month
                click_count = year + month
            return click_count, i_day


class LufthansaDownloaderMiddleware:
    def __init__(self, log, resource, target, is_select_date, format_date):
        self.log = log
        self.resource = resource
        self.target = target
        self.is_select_date = is_select_date
        self.format_date = format_date

    @classmethod
    def from_crawler(cls, crawler):
        log = crawler.spider.logger
        resource = crawler.settings.get('RESOURCE', 'shanghai')
        target = crawler.settings.get('TARGET', 'frankfurt')
        is_select_date = crawler.settings.getbool('IS_SELECT_DATE', False)
        format_date = crawler.settings.get('FORMAT_DATE', None)
        return cls(log, resource, target, is_select_date, format_date)

    async def get(self, url, is_select_date):
        response = list()
        async with async_playwright() as playwright:
            try:
                iphone = playwright.devices['iPhone 12 Pro']
                browser = await playwright.chromium.launch(headless=False, proxy={
                    'server': 'http://127.0.0.1:8080'
                })
                try:
                    new_context = await browser.new_context(**iphone)
                    url = url
                    for count in range(1
                                       ):
                        try:

                            page = await new_context.new_page()
                            js = """
                                        Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
                                     """
                            try:
                                await page.add_init_script(js)
                                await page.goto(url=url, timeout=30000)
                                i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
                                if i_agree:
                                    await page.click("div.buttonView>div>button#cm-acceptAll")

                                await asyncio.sleep(0.7)
                                await page.fill('div.input-border-wrapper>input[placeholder="From"]', self.resource)
                                await asyncio.sleep(2)
                                await page.keyboard.press('Enter')

                                await asyncio.sleep(0.7)
                                await page.click('label[class="custom-control custom-checkbox"]')

                                await asyncio.sleep(0.7)
                                await page.fill('div.input-border-wrapper>input[placeholder="To"]', self.target)
                                await asyncio.sleep(2)
                                await page.keyboard.press('Enter')

                                # 日期输入
                                if is_select_date:
                                    formatdate = FormatDate(datetimer=self.format_date)
                                    click_count_day = formatdate.is_date()
                                    count = click_count_day[0]
                                    day = click_count_day[1]
                                    if count != 0:
                                        await page.click('input[placeholder="Departure date is required"]')
                                        while count > 0:
                                            await page.click(
                                                'button[class="DayPickerNavigation_button DayPickerNavigation_button_1 DayPickerNavigation_button__vertical DayPickerNavigation_button__vertical_2"]:nth-child(2)')
                                            await asyncio.sleep(0.7)
                                            count -= 1
                                    await asyncio.sleep(0.7)
                                    await page.click(
                                        f'//div[@class="CalendarMonth CalendarMonth_1" and @data-visible="true"]//td[@class="CalendarDay CalendarDay_1 CalendarDay__default CalendarDay__default_2" and contains(string(),"{day}")]')
                                    # await page.click(f'td:contains("{day}")')
                                    # await page.click(f'td:has-text("{day}")')
                                    # await page.click('td:text("28"):nth-child(2)')
                                await asyncio.sleep(2)

                                # 搜索票数
                                await page.wait_for_selector('button[class="btn btn-primary"]')
                                await page.click('button[class="btn btn-primary"]')

                                # 当天没有，查找往后7天的
                                await asyncio.sleep(1.5)
                                h1 = await page.text_content('h1:nth-child(1)')
                                if re.findall('.*Flight search.*', h1):
                                    await page.evaluate("document.getElementsByTagName('button')[0].click()")
                                    await asyncio.sleep(3)
                                    count = 0
                                    new_page = await page.text_content('h1:nth-child(1)')
                                    while count < 7:
                                        if re.findall('.*Flight search.*', new_page):
                                            await page.evaluate("document.getElementsByTagName('button')[0].click()")
                                            await asyncio.sleep(3)
                                            new_page = await page.text_content('h1:nth-child(1)')
                                        else:
                                            await page.close()
                                        count += 1

                                await page.click('div[class="flight-info lowest-price"]:nth-child(1)', timeout=40000)
                                await page.click(
                                    'div[class="booking-class_tabs-content booking-class_tabs-content--e"]:nth-child(1)')
                                await page.click('button[class="sn-touchable on   primary    full-width"]')

                                await asyncio.sleep(1.5)
                                await page.click('a#checkout-link')

                                train = await page.query_selector(
                                    'div[class="lh-lightbox priority-lightbox "][id="div-2"]>a:nth-child(1)')
                                if train:
                                    await page.click('div[class="lh-lightbox priority-lightbox"]>a:nth-child(1)', timeout=40000)
                                    await asyncio.sleep(1.5)
                                    await page.click('div[class="secondary-column-child"]>a:nth-child(2)')
                                context = await page.content()
                                response.append(context)
                                not_network = await page.wait_for_load_state('networkidle')
                                if not_network:
                                    await page.close()
                            except TimeoutError:
                                await page.close()
                        finally:
                            await page.close()
                finally:
                    await new_context.close()
            finally:
                await browser.close()
            return response

    async def process_request(self, request, spider):
        try:
            result = await asyncio.create_task(self.get(url=request.url, is_select_date=self.is_select_date))
            return HtmlResponse(url=request.url, body=result, request=request, status=200, encoding="utf-8")
        except Exception as e:
            spider.logger.info(f"Error {e}!")
        # try:
        #     results = await asyncio.create_task(self.get(url=request.url))
        #     for result in results:
        #         return HtmlResponse(url=request.url, body=result, request=request, status=200, encoding="utf-8")
        # except Exception as e:
        #     spider.logger.info(f"Error {e}!")

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
