import json
import re
import datetime
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from xml.dom import minidom

def clean_text(text):
    """
    Yahooリアルタイム検索特有の強調マーク (START ... END) を除去し、
    余分な空白を整理し、XMLで無効な制御文字を除去する
    """
    if not text:
        return ""
    
    # 1. 強調マークの除去
    text = re.sub(r'START\s+', '', text)
    text = re.sub(r'\s+END', '', text)
    
    # 2. XMLで無効な制御文字（タブ、改行、復帰以外）を除去
    # valid_xml_chars は XML 1.0 仕様に基づく
    # [#x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]]
    text = "".join(ch for ch in text if 
        unicodedata.category(ch)[0] != "C" or ch in "\t\n\r"
    )
    
    # 3. 連続する空白を1つにまとめる
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_rfc822_date(timestamp):
    """
    UNIXタイムスタンプをRSS標準のRFC822形式に変換
    """
    dt = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')

def fetch_realtime_search(query):
    """
    指定されたキーワードでYahoo!リアルタイム検索を実行し、HTMLを取得する
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://search.yahoo.co.jp/realtime/search?p={encoded_query}"
    
    # ブラウザからのアクセスに見せるためのヘッダー
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def clean_url(url):
    """
    URLからクエリパラメータ（?以降）を除去して、純粋な投稿URLにする
    """
    if not url:
        return ""
    return url.split('?')[0]

def generate_rss_from_html(html_content, query, output_file):
    """
    HTML文字列からJSONを抽出し、RSSフィードを生成する
    """
    # JSONデータを抽出
    match = re.search(r'<script id=\"__NEXT_DATA__\"\s+type=\"application/json\">(.*?)</script>', html_content, re.DOTALL)
    if not match:
        print("Error: Could not find JSON data in the fetched page.")
        return

    data = json.loads(match.group(1))
    page_data = data.get('props', {}).get('pageProps', {}).get('pageData', {})
    entries = page_data.get('timeline', {}).get('entry', [])

    # RSSの基本構造を作成
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    title_el = ET.SubElement(channel, 'title')
    title_el.text = f"Yahoo!リアルタイム検索 - {query}"

    link_el = ET.SubElement(channel, 'link')
    link_el.text = f"https://search.yahoo.co.jp/realtime/search?p={urllib.parse.quote(query)}"

    desc_el = ET.SubElement(channel, 'description')
    desc_el.text = f"Latest search results for '{query}' on Yahoo! Realtime Search"

    for entry in entries:
        item = ET.SubElement(channel, 'item')
        
        raw_text = entry.get('displayText', '')
        text = clean_text(raw_text)
        user_name = entry.get('name', 'Unknown')
        
        # クリーンなURLを取得
        raw_url = entry.get('url', '')
        url = clean_url(raw_url)
        
        # タイトル (本文のみ)
        item_title = ET.SubElement(item, 'title')
        item_title.text = text

        # リンク (パラメータなし)
        item_link = ET.SubElement(item, 'link')
        item_link.text = url

        # 本文 (ユーザー名: 本文)
        item_desc = ET.SubElement(item, 'description')
        item_desc.text = f"{user_name}: {text}"

        # 投稿日時
        item_date = ET.SubElement(item, 'pubDate')
        created_at = entry.get('createdAt')
        if created_at:
            item_date.text = format_rfc822_date(created_at)

        # GUID (パラメータなし)
        item_guid = ET.SubElement(item, 'guid', isPermaLink='true')
        item_guid.text = url

    # XMLを整形
    xml_string = ET.tostring(rss, encoding='utf-8')
    parsed_xml = minidom.parseString(xml_string)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding='utf-8')

    with open(output_file, 'wb') as f:
        f.write(pretty_xml)
    
    print(f"Successfully generated: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_rss.py <search_query>")
        sys.exit(1)

    search_query = sys.argv[1]
    
    # ファイル名用のクリーンアップ
    # 1. 引用符を除去
    # 2. スペースをアンダーバーに置換
    # 3. その他の使用不可文字を除去
    filename_part = search_query.replace('"', '').replace("'", "")
    filename_part = re.sub(r'\s+', '_', filename_part)
    safe_filename = re.sub(r'[\\/*?:"<>|]', '', filename_part)
    
    if not safe_filename:
        safe_filename = "search_result"
        
    output_filename = f"rss_{safe_filename}.xml"

    try:
        html = fetch_realtime_search(search_query)
        generate_rss_from_html(html, search_query, output_filename)
    except Exception as e:
        print(f"An error occurred: {e}")
