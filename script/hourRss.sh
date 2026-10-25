#!/bin/bash

OUTPUT_FILE="hour.xml"
MAX_ITEMS=10

GUID=$(date "+%y%m%d%H%M%S")
CURRENT_HOUR=$(date "+%H")
ITEM_TITLE="▼ ${CURRENT_HOUR}"

# 既存のXMLファイルがある場合、過去の <item>...</item> を最大 (MAX_ITEMS - 1) 件抽出する
EXISTING_ITEMS=""
if [ -f "$OUTPUT_FILE" ]; then
  EXISTING_ITEMS=$(awk -v max=$((MAX_ITEMS - 1)) '
    /<item>/ { in_item=1; count++ }
    in_item && count <= max { print }
    /<\/item>/ {
      if (in_item && count <= max) print ""
      in_item=0
    }
  ' "$OUTPUT_FILE")
fi

# 新しいアイテムを先頭にし、各 </item> の下に空行を入れて書き出す
{
  cat <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>毎時フィード</title>
    <link>https://github.com/staddss/rss</link>
    <description></description>
    <language>ja</language>

    <item>
      <title>${ITEM_TITLE}</title>
      <link>https://www.google.co.jp/search?q=${GUID}</link>
      <description></description>
      <pubDate></pubDate>
      <guid>${GUID}</guid>
    </item>

EOF
  if [ -n "$EXISTING_ITEMS" ]; then
    printf "%s\n\n" "$EXISTING_ITEMS"
  fi
  cat <<EOF
  </channel>
</rss>
EOF
} > "$OUTPUT_FILE"
