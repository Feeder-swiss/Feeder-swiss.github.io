#!/usr/bin/env python3
import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import pytz

SOURCES = {
    'Reuters EU': 'https://feeds.reuters.com/reuters/worldNews',
    'BBC Europe': 'http://feeds.bbc.co.uk/news/world/europe/rss.xml',
    'Politico Europe': 'https://www.politico.eu/feed/',
    'Euractiv': 'https://www.euractiv.com/feed/',
    'SRF News': 'https://www.srf.ch/news/bnews/rss/2c835f36-c934-4e31-aa35-08732e97af5e',
    'Swissinfo': 'https://www.swissinfo.ch/feed/rss/latest',
}

def fetch_and_aggregate():
    all_items = []
    
    for source_name, feed_url in SOURCES.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                all_items.append({
                    'title': entry.get('title', 'Untitled'),
                    'link': entry.get('link', ''),
                    'description': entry.get('summary', '')[:500],
                    'pubDate': entry.get('published', datetime.now(pytz.UTC).isoformat()),
                    'source': source_name,
                    'guid': entry.get('id', entry.get('link', source_name))
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue
    
    try:
        all_items.sort(key=lambda x: x['pubDate'], reverse=True)
    except:
        pass
    
    rss = Element('rss', {
        'version': '2.0',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = 'EU & Swiss News Curator'
    SubElement(channel, 'link').text = 'https://github.com'
    SubElement(channel, 'description').text = 'Curated news and analysis on EU governance, Swiss politics, and regional events'
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.now(pytz.UTC).strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', 'https://github.com')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    for item in all_items[:50]:
        item_elem = SubElement(channel, 'item')
        SubElement(item_elem, 'title').text = f"[{item['source']}] {item['title']}"
        SubElement(item_elem, 'link').text = item['link']
        SubElement(item_elem, 'guid').text = item['guid']
        SubElement(item_elem, 'pubDate').text = str(item['pubDate'])
        SubElement(item_elem, 'description').text = item['description']
        SubElement(item_elem, 'category').text = item['source']
    
    xml_str = tostring(rss, encoding='unicode')
    with open('eu-swiss-feed.xml', 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_str)
    
    print(f"Feed generated with {len(all_items)} items")

if __name__ == '__main__':
    fetch_and_aggregate()
