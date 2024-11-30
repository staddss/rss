#!/bin/bash

OUTPUT_FILE="date.xml"
GUID=$(date +"%y%m%d%H%M%S")
TODAY_DATE=$(date +"%Y/%m/%d")
WEEK=$(date '+%a')
ITEM_TITLE="▼ ${TODAY_DATE} (${WEEK})"

cat <<EOF > "$OUTPUT_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>日次フィード</title>
    <link>https://github.com/staddss/rss</link>
    <description></description>
    <language>ja</language>

    <item>
      <title>${ITEM_TITLE}</title>
      <link>https://github.com/staddss/rss</link>
      <description></description>
      <pubDate></pubDate>
      <guid>${GUID}</guid>
    </item>

  </channel>
</rss>
EOF
