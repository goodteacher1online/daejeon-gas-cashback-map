# 대전 온통대전 주유소 실시간 유가 지도

온통대전(대전사랑카드) 캐시백 대상 주유소·LPG충전소 9곳의 유가를 지도에서 확인합니다.

- `index.html` — 지도 페이지 (GitHub Pages로 서빙)
- `latest_station_prices.json` — GitHub Actions가 주기적으로 갱신하는 유가 스냅샷
- `scripts/update_prices.py` — 카카오맵에서 유가를 스크래핑해 위 두 파일을 갱신하는 스크립트
- `.github/workflows/update-prices.yml` — 하루 2회(07:00 / 16:00 KST) 자동 실행

가격은 스크래핑 시점 기준이며, 실제 판매가는 매장 게시 가격을 우선합니다.
