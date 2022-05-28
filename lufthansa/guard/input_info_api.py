import re
from playwright.async_api import async_playwright
import asyncio
from loguru import logger
import json


async def start_one_page(page, url):
    js = """
        Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
        """
    try:
        await page.add_init_script(js)
        await page.goto(url=url, timeout=30000)
        not_network = await page.wait_for_load_state('networkidle')
        if not_network:
            await page.close()
        i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
        if i_agree:
            await page.click("div.buttonView>div>button#cm-acceptAll")
    finally:
        await asyncio.sleep(1.5)
        logger.info('page table close!')
        await page.close()


async def start_two_page(page, url):
    js = """
        Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
        """
    try:
        await page.add_init_script(js)
        await page.goto(url=url, timeout=30000)
        not_network = await page.wait_for_load_state('networkidle')
        if not_network:
            await page.close()
        i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
        if i_agree:
            await page.click("div.buttonView>div>button#cm-acceptAll")
        # await asyncio.sleep(200)
    finally:
        await asyncio.sleep(1.5)
        logger.info('page table close!')
        await page.close()


async def start_three_page(page, url):
    js = """
        Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
        """
    try:
        await page.add_init_script(js)
        await page.goto(url=url, timeout=30000)
        i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
        if i_agree:
            await page.click("div.buttonView>div>button#cm-acceptAll")

        first_name = await page.query_selector('input#ADT_0_firstName')
        if first_name:
            await first_name.fill("yourfirstname")

        last_name = await page.query_selector('input#ADT_0_lastName')
        if last_name:
            await last_name.fill('yourlastname')
        await asyncio.sleep(0.5)
        phone_ = await page.query_selector(
            'input[id="contactPoint.phonePhoneNumber"][name="contactPoint.phone.phoneNumber"]')
        if phone_:
            phone_.fill('911')

        email = await page.query_selector('input[id="contactPointEmail"][type="email"]')
        if email:
            await email.fill('your@email.com')
        await page.click(
            'div[class="formErrorContainer   "][id="checkbox-container-additional_conf"] input[type="checkbox"]:nth-child(2)')
        # await asyncio.sleep(0.5)
        # await page.click('input[type="checkbox"]:nth-child(3)')
        # await asyncio.sleep(0.5)
        # await page.click('input[type="checkbox"]:nth-child(4)')

    finally:
        await asyncio.sleep(250)
        logger.info('page table close!')
        await page.close()


async def main():
    async with async_playwright() as playwright:
        iphone = playwright.devices['iPhone 13 Pro Max']
        browser = await playwright.chromium.launch(headless=False, proxy={
            'server': 'http://127.0.0.1:8088'
        })
        new_context = await browser.new_context(**iphone)
        # one_page = await new_context.new_page()
        # two_page = await new_context.new_page()
        three_page = await new_context.new_page()
        with open('lufthansa_re.json') as fp:
            request_body = fp.readlines()
            for request in request_body:
                headers = json.loads(request.replace('\n', ''))
                url = headers.get('url')
                # if re.search(r'^https://.*/rs/.+?execution=.+2&l=en$', url):
                #     logger.info(url)
                #     await start_one_page(page=one_page, url=url)
                # elif re.search(r'^https://.*/rs/.+?execution=.+1&l=en$', url):
                #     logger.info(url)
                #     await start_two_page(page=two_page, url=url)
                # else:
                logger.info(url)

                await start_three_page(page=three_page, url=url)
        await asyncio.sleep(2000)
        await new_context.close()
        await browser.close()


asyncio.run(main())
