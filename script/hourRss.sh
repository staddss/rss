#!/bin/bash

OUTPUT_FILE="hour.xml"
GUID=$(date "+%y%m%d%H%M%S")
CURRENT_HOUR=$(date "+%H")
ITEM_TITLE="▼ ${CURRENT_HOUR}"

cat <<EOF > "$OUTPUT_FILE"
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

  </channel>
</rss>
EOF
