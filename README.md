# sample-scrapy

netkeibaの出馬表ページ（1レース）を対象にスクレイピングするためのScrapyプロジェクトです。

## セットアップ

```bash
pip install scrapy
```

## 使い方

```bash
cd horse_racing_crawler
OUTPUT_DIR=./output CACHE_DIR=./httpcache scrapy crawl NetkeibaSpider -a start_url=https://race.netkeiba.com/race/shutuba.html?race_id=202506050811
```

```bash
cd horse_racing_crawler
OUTPUT_DIR=./output CACHE_DIR=./httpcache scrapy crawl NetkeibaSpider -a start_url=https://db.netkeiba.com/horse/2021110048/
```

- 出力先は `${OUTPUT_DIR}/race_{race_id}.json.gz` です。
- HTTPキャッシュは `.json.gz` 形式で `${CACHE_DIR}` に保存されます。
- 欠損値は `null` で出力されます。
- `start_url` が必須です。
- `start_url` の対応URL種別は以下の通りです。
  - 出馬表: `https://race.netkeiba.com/race/shutuba.html?race_id=...`
  - 馬: `https://db.netkeiba.com/horse/<id>/`
  - 騎手: `https://db.netkeiba.com/jockey/(result/recent/)?<id>/`
  - 厩舎: `https://db.netkeiba.com/trainer/(result/recent/)?<id>/`

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

## Spider Contractsによるチェック

Spider Contractsは `db.netkeiba.com` のページに対して `scrapy check` を実行します。
GitHub Actionsで実行するため、手元での実行が必要な場合はネットワークアクセスが可能な環境で以下を実行してください。

```bash
cd horse_racing_crawler
scrapy check NetkeibaSpider
```
