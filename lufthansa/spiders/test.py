# import time
# from playwright.async_api import async_playwright
# import asyncio
# from loguru import logger
# from fake_useragent import FakeUserAgent
# from random import choice
# import re
#
#
# async def main():
#     async with async_playwright() as playwright:
#         iphone = playwright.devices['iPhone 13 Pro Max']
#         browser = await playwright.chromium.launch(headless=False, proxy={
#             'server': 'socks://172.17.0.2:7890'
#         })
#
#         new_context = await browser.new_context(**iphone)
#         try:
#             for i in range(2):
#                 ua = choice(FakeUserAgent().data_browsers.get('chrome'))
#                 logger.debug(ua)
#                 page = await new_context.new_page()
#                 js = """
#                 Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
#                 """
#                 try:
#                     await page.add_init_script(js)
#                     await page.goto("https://www.lufthansa.com", timeout=30000)
#                     i_agree = await page.query_selector("div.buttonView>div>button#cm-acceptAll")
#                     if i_agree:
#                         await page.click("div.buttonView>div>button#cm-acceptAll")
#
#                     await asyncio.sleep(0.7)
#                     await page.fill('div.input-border-wrapper>input[placeholder="From"]', 'fuzhou')
#                     await asyncio.sleep(0.7)
#                     await page.keyboard.press('Enter')
#
#                     await asyncio.sleep(0.7)
#                     await page.click('label[class="custom-control custom-checkbox"]')
#
#                     await asyncio.sleep(0.7)
#                     await page.fill('div.input-border-wrapper>input[placeholder="To"]', 'frankfurt')
#                     await asyncio.sleep(0.7)
#                     await page.keyboard.press('Enter')
#
#                     await page.wait_for_selector('button[class="btn btn-primary"]')
#                     await page.click('button[class="btn btn-primary"]')
#
#                     await asyncio.sleep(1.5)
#                     h1 = await page.text_content('h1:nth-child(1)')
#                     if re.findall('.*Flight search.*', h1):
#                         await page.evaluate("document.getElementsByTagName('button')[0].click()")
#                         # 点击第三个"Buy"按钮page.click(":nth-match(:text('Buy'), 3)"
#                         await asyncio.sleep(3)
#                         new_page = await page.text_content('h1:nth-child(1)')
#                         while True:
#                             if re.findall('.*Flight search.*', new_page):
#                                 await page.evaluate("document.getElementsByTagName('button')[0].click()")
#                                 await asyncio.sleep(3)
#                             else:
#                                 break
#
#                     await page.click('div[class="flight-info lowest-price"]:nth-child(1)')
#                     await page.click(
#                         'div[class="booking-class_tabs-content booking-class_tabs-content--e"]:nth-child(1)')
#                     await page.click('button[class="sn-touchable on   primary    full-width"]')
#
#                     await asyncio.sleep(1.5)
#                     await page.click('a#checkout-link')
#
#                     train = await page.query_selector(
#                         'div[class="lh-lightbox priority-lightbox "][id="div-2"]>a:nth-child(1)')
#                     if train:
#                         await page.click('div[class="lh-lightbox priority-lightbox"]>a:nth-child(1)')
#                         await asyncio.sleep(1.5)
#                         await page.click('div[class="secondary-column-child"]>a:nth-child(2)')
#                 except TimeoutError as e:
#                     logger.debug(f"error {e}")
#                     await page.close()
#
#         finally:
#             await asyncio.sleep(100)
#         await browser.close()
#
#
# asyncio.run(main())
