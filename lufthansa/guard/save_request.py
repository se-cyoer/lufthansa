import time
from playwright.async_api import async_playwright
import asyncio
from loguru import logger
import re
from argparse import ArgumentParser
import datetime
import sys
import signal


def quit(signum, frame):
    logger.debug('Stop yes!')
    sys.exit()


def parsel():
    today = datetime.date.today()  # 获得今天的日期
    # yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    parser = ArgumentParser(description="启动抓取接口进程,守护进程")
    parser.add_argument('--is_select_date', type=bool, default=False, help='gnu.py --is_select_date True (是否需要指定日期，默认为不指定，需要抓取指定日期，在参数后边添加 True)')
    parser.add_argument('--formatdate', type=str, default=f'{tomorrow}', help=f'gnu.py --formatdate {tomorrow} (指定抓取的日期，不指定默认明天)')
    parser.add_argument('--source', type=str, default='shanghai', help='gnu.py --source shanghai (指定起点，默认上海)')
    parser.add_argument('--target', type=str, default='frankfurt', help='gnu.py --target frankfurt (指定落点，默认法兰克)')
    args = parser.parse_args()
    return args


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


async def start_page(is_select_date, click_count_day, source, target):
    async with async_playwright() as playwright:
        iphone = playwright.devices['iPhone 11']
        browser = await playwright.chromium.launch(headless=False, proxy={
            'server': 'http://127.0.0.1:8080'
            })

        new_context = await browser.new_context(**iphone)
        try:
            for i in range(1):
                page = await new_context.new_page()
                js = """
                Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
                """
                try:
                    await page.add_init_script(js)
                    await page.goto("https://www.lufthansa.com", timeout=30000)
                    i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
                    if i_agree:
                        await page.click("div.buttonView>div>button#cm-acceptAll")

                    await asyncio.sleep(0.7)
                    await page.fill('div.input-border-wrapper>input[placeholder="From"]', source)
                    await asyncio.sleep(2)
                    await page.keyboard.press('Tab')

                    await asyncio.sleep(0.7)
                    await page.click('label[class="custom-control custom-checkbox"]')

                    await asyncio.sleep(0.7)
                    await page.fill('div.input-border-wrapper>input[placeholder="To"]', target)
                    await asyncio.sleep(2)
                    await page.keyboard.press('Enter')
                    await asyncio.sleep(0.5)
                    # 日期输入
                    if is_select_date:
                        count = click_count_day[0]
                        day = click_count_day[1]
                        if count != 0:
                            await page.click('input[placeholder="Departure date is required"]')
                            while count > 0:
                                await page.click(
                                        'button[class="DayPickerNavigation_button DayPickerNavigation_button_1 '
                                        'DayPickerNavigation_button__vertical DayPickerNavigation_button__vertical_2"]'
                                        ':nth-child(2)')
                                await asyncio.sleep(0.7)
                                count -= 1
                        await asyncio.sleep(0.7)
                        await page.click(
                                f'//div[@class="CalendarMonth CalendarMonth_1" and @data-visible="true"]//'
                                f'td[@class="CalendarDay CalendarDay_1 CalendarDay__default CalendarDay__default_2"'
                                f' and contains(string(),"{day}")]')
                        # await page.click(f'td:contains("{day}")')
                        # await page.click(f'td:has-text("{day}")')
                        # await page.click('td:text("28"):nth-child(2)')
                    await asyncio.sleep(2)

                    await page.wait_for_selector('button[class="btn btn-primary"]')
                    await page.click('button[class="btn btn-primary"]')

                    await asyncio.sleep(1.5)
                    h1 = await page.text_content('h1:nth-child(1)')
                    if re.findall('.*Flight search.*', h1):
                        await page.evaluate("document.getElementsByTagName('button')[0].click()")
                        # 点击第三个"Buy"按钮page.click(":nth-match(:text('Buy'), 3)"
                        await asyncio.sleep(3)
                        new_page = await page.text_content('h1:nth-child(1)')
                        while True:
                            if re.findall('.*Flight search.*', new_page):
                                await page.evaluate("document.getElementsByTagName('button')[0].click()")
                                await asyncio.sleep(3)
                            else:
                                await page.close()

                    await page.click('div[class="flight-info lowest-price"]:nth-child(1)')
                    await page.click(
                            'div[class="booking-class_tabs-content booking-class_tabs-content--e"]:nth-child(1)')
                    await page.click('button[class="sn-touchable on   primary    full-width"]')

                    await asyncio.sleep(1.5)
                    await page.click('a#checkout-link')

                    train = await page.query_selector(
                            'div[class="lh-lightbox priority-lightbox "][id="div-2"]>a:nth-child(1)')
                    if train:
                        await page.click('div[class="lh-lightbox priority-lightbox"]>a:nth-child(1)')
                        await asyncio.sleep(1.5)
                        await page.click('div[class="secondary-column-child"]>a:nth-child(2)')
                except TimeoutError as e:
                    logger.debug(f"error {e}")
                    await page.close()
        except Exception as e:
            logger.debug(f"error {e}")
        time.sleep(5)
        await new_context.close()
        await browser.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    args = parsel()
    source = args.source
    target = args.target
    date = args.formatdate
    is_select_date = args.is_select_date
    formatdate = FormatDate(date)
    click_count_day = formatdate.is_date()
    while True:
        time.sleep(1)
        asyncio.run(
                start_page(is_select_date=is_select_date, click_count_day=click_count_day, source=source, target=target))
