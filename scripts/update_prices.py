# -*- coding: utf-8 -*-
"""
온통대전 주유소 실시간 가격 자동 최신화 스크립트 (GitHub Actions용)
카카오맵 개별 매장 페이지를 스크래핑해 index.html의 STATIONS 배열과
latest_station_prices.json을 갱신한다.
"""

import asyncio, os, sys, re, json, datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KST = datetime.timezone(datetime.timedelta(hours=9))

TARGETS = [
    {"id": 1, "name": "에이스주유소", "url": "https://place.map.kakao.com/1445954313"},
    {"id": 2, "name": "가수원주유소", "url": "https://map.kakao.com/?q=대전+서구+계백로+1176+가수원주유소"},
    {"id": 3, "name": "대동현대주유소", "url": "https://place.map.kakao.com/1439720917"},
    {"id": 4, "name": "방동주유소", "url": "https://place.map.kakao.com/11069446"},
    {"id": 5, "name": "만년교셀프주유소", "url": "https://place.map.kakao.com/10345384"},
    {"id": 6, "name": "구암상사주유소", "url": "https://place.map.kakao.com/8707044"},
    {"id": 7, "name": "회덕IC충전소", "url": "https://place.map.kakao.com/17156998"},
    {"id": 8, "name": "유한가스충전소", "url": "https://place.map.kakao.com/12548590"},
    {"id": 9, "name": "황제충전소", "url": "https://place.map.kakao.com/18377713"}
]

def safe_parse(pat, text):
    m = re.search(pat, text)
    if m:
        val_str = m.group(1).replace(',', '').strip()
        if val_str.isdigit():
            return int(val_str)
    return None

async def fetch_prices():
    print("⚡ 온통대전 6개 주유소 및 3개 충전소의 최신 유가를 수집 중입니다...")
    prices = {}
    now_str = datetime.datetime.now(KST).strftime("%Y.%m.%d %H:%M")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        for t in TARGETS:
            try:
                await page.goto(t['url'], wait_until="networkidle", timeout=20000)
                await asyncio.sleep(1)
                text = await page.evaluate("() => document.body.innerText")

                g = safe_parse(r'휘발유\s*([0-9,]{4,6})', text)
                d = safe_parse(r'경유\s*([0-9,]{4,6})', text)
                l = safe_parse(r'LPG\s*([0-9,]{4,6})', text)

                prices[t['id']] = {
                    "name": t['name'],
                    "gasoline": g,
                    "diesel": d,
                    "lpg": l,
                    "updatedAt": now_str
                }
                print(f"  ✓ {t['name']}: 휘발유={g}원, 경유={d}원, LPG={l}원")
            except Exception as e:
                print(f"  ⚠ {t['name']} 오류 (기존 유지): {e}")

        await browser.close()

    return prices, now_str

def to_js_val(v):
    return str(v) if v is not None else "null"

def update_html_file(html_path, prices, now_str):
    if not os.path.exists(html_path):
        return False

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    for st_id, p in prices.items():
        if p["gasoline"] is not None or p["lpg"] is not None:
            pattern = rf'(id:\s*{st_id},[\s\S]*?fuel:\s*\{{)\s*gasoline:\s*[0-9a-zA-Z]+,\s*diesel:\s*[0-9a-zA-Z]+,\s*lpg:\s*[0-9a-zA-Z]+(\s*\}})'
            g_str = to_js_val(p["gasoline"])
            d_str = to_js_val(p["diesel"])
            l_str = to_js_val(p["lpg"])
            repl = rf'\g<1> gasoline: {g_str}, diesel: {d_str}, lpg: {l_str}\2'
            content = re.sub(pattern, repl, content)

    content = re.sub(r'id="syncTime">[^<]*</span>', f'id="syncTime">최근 갱신: {now_str}</span>', content)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✓ {os.path.basename(html_path)} 최신 유가 갱신 완료! ({now_str})")
    return True

async def main():
    prices, now_str = await fetch_prices()

    html_path = os.path.join(REPO_ROOT, "index.html")
    update_html_file(html_path, prices, now_str)

    json_path = os.path.join(REPO_ROOT, "latest_station_prices.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"updatedAt": now_str, "prices": prices}, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 모든 주유소 유가가 최신({now_str})으로 성공적으로 갱신되었습니다!")

if __name__ == "__main__":
    asyncio.run(main())
