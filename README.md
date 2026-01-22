# sample-scrapy

netkeibaの出馬表ページ（1レース）を対象にスクレイピングするためのScrapyプロジェクトです。

## セットアップ

```bash
pip install scrapy boto3
```

## 使い方

### S3互換ストレージ出力

```bash
cd horse_racing_crawler
S3_ENDPOINT_URL=https://minio.example.com \
S3_ACCESS_KEY_ID=your-access-key \
S3_SECRET_ACCESS_KEY=your-secret-key \
S3_REGION_NAME=us-east-1 \
S3_BUCKET=netkeiba-data \
S3_HTTP_CACHE_PREFIX=httpcache \
S3_FEEDS_PREFIX=feeds \
scrapy crawl NetkeibaSpider -a start_url=https://race.netkeiba.com/race/shutuba.html?race_id=202506050811
```

#### S3互換ストレージ用の環境変数

| 変数 | 説明 |
| --- | --- |
| `S3_ENDPOINT_URL` | S3互換ストレージのエンドポイントURL |
| `S3_ACCESS_KEY_ID` | アクセスキー |
| `S3_SECRET_ACCESS_KEY` | シークレットキー |
| `S3_REGION_NAME` | リージョン（既定: `us-east-1`） |
| `S3_BUCKET` | 対象バケット |
| `S3_HTTP_CACHE_PREFIX` | HTTPキャッシュの保存先プレフィックス |
| `S3_FEEDS_PREFIX` | クロール結果の保存先プレフィックス |
HTTPキャッシュは `aa/<hash>.json.gz` のように先頭2文字で1階層に分散します。

- S3互換ストレージ出力時は `s3://$S3_BUCKET/$S3_FEEDS_PREFIX/race_{race_id}.json.gz` に保存されます。
- S3互換ストレージのHTTPキャッシュは `s3://$S3_BUCKET/$S3_HTTP_CACHE_PREFIX/<shard>/...` に保存されます。
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
