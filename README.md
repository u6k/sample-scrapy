# sample-scrapy

netkeibaの出馬表ページ（1レース）を対象にスクレイピングするためのScrapyプロジェクトです。

## セットアップ

```bash
pip install scrapy
```

## 使い方

```bash
cd horse_racing_crawler
OUTPUT_DIR=./output CACHE_DIR=./httpcache scrapy crawl NetkeibaSpider -a race_id=202506050811
```

- 出力先は `${OUTPUT_DIR}/race_{race_id}.json.gz` です。
- HTTPキャッシュは `.json.gz` 形式で `${CACHE_DIR}` に保存されます。
- 欠損値は `null` で出力されます。

## 取得項目

- race_id
- bracket_number
- horse_number
- horse_id
- horse_name
- jockey_weight
- jockey_id
- jockey_name
- trainer_id
- trainer_name
- horse_weight
- horse_weight_diff
