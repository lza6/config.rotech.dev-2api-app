import asyncio, sys
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width":1100,"height":800})
        await pg.goto("http://127.0.0.1:8941/", wait_until="networkidle")
        await pg.fill("#input", "用中文回答：列出3种编程语言，每行一个，不要序号")
        await pg.select_option("#model", "openchat-gpt5")
        await pg.click("#send")
        # 等待机器人气泡出现时长文本
        for _ in range(60):
            await pg.wait_for_timeout(1000)
            txt = await pg.eval_on_selector_all(".msg.bot .bubble", "els=>els.map(e=>e.innerText).join('|')")
            if "思考中" not in txt and len(txt) > 40:
                break
        await pg.screenshot(path="ui_demo.png", full_page=True)
        out = await pg.eval_on_selector_all(".msg .bubble", "els=>els.map(e=>e.innerText)")
        print("BUBBLES:", out)
        stat = await pg.inner_text("#stat")
        print("STAT:", stat)
        await b.close()

asyncio.run(main())
