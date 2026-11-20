# 風景印地圖・東京

在地圖上查看東京哪些郵局有風景印，並記錄自己收集了哪些。手機優先設計，電腦也能使用。

## 功能

- 地圖顯示東京都所有有風景印的郵局（紅點：未收集／綠點：已收集／橘圈：即將廢止或新圖案）
- 📍 定位，以及依距離排序的「附近清單」
- 每款風景印可分別標記「已收集」並記錄日期
- 依狀態、地區篩選，搜尋郵局名或地名
- Google Maps 導航、查營業時間
- 收集紀錄存在瀏覽器裡，可匯出／匯入備份檔

## 資料來源

- 風景印資料：[日本郵便「風景印」](https://www.post.japanpost.jp/enjoy/culture/stamp/fuke/)
- 地址轉座標：國土地理院 地址搜尋 API
- 地圖：[OpenFreeMap](https://openfreemap.org/)（© OpenMapTiles，資料來自 © OpenStreetMap contributors）
- 地圖程式庫：[MapLibre GL JS](https://maplibre.org/)（BSD-3-Clause，見 `vendor/LICENSE.txt`）

風景印會新增或廢止，實際狀況請以日本郵便官網為準。

## 更新資料

```bash
python3 scripts/fetch_list.py raw/tokyo_list.json
python3 scripts/fetch_detail.py raw/tokyo_list.json raw/tokyo_detail.json   # 約 15 分鐘，每頁間隔 1 秒
python3 scripts/build_data.py raw/tokyo_detail.json data/tokyo.json
```

需要能連到 `www.post.japanpost.jp` 和 `msearch.gsi.go.jp`。`raw/geocode_cache.json` 是座標的快取，可以加快更新速度。
