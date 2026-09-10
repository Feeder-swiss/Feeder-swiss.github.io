#!/usr/bin/env python3
import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# Proven working feeds - relaxed filtering
SOURCES = {
    'Politico Europe': 'https://www.politico.eu/feed/',
    'Reuters': 'https://feeds.reuters.com/reuters/worldNews',
    'BBC Europe': 'http://feeds.bbc.co.uk/news/world/europe/rss.xml',
    'DW': 'https://rss.dw.com/xml/rss-en-eu',
    'AP News': 'https://apnews.com/apf-services/APNewsFeeds?category=world&subcategory=europe&outputType=rss',
    'NZZ': 'https://www.nzz.ch/feed',
    'Euractiv': 'https://www.euractiv.com/feed/',
    'Financial Times': 'https://www.ft.com/?format=rss',
    'Tages-Anzeiger': 'https://www.tagesanzeiger.ch/feed',
    'SRF': 'https://www.srf.ch/news/bnews/rss/2c835f36-c934-4e31-aa35-08732e97af5e',
    'Swissinfo': 'https://www.swissinfo.ch/feed/rss/latest',
    'ECFR': 'https://ecfr.eu/feed/',
    'EU Observer': 'https://euobserver.com/feed',
}

def fetch_and_aggregate():
    all_items = []
    working_sources = []
    broken_sources = []
    
    print("Starting feed aggregation...\n")
    
    for source_name, feed_url in SOURCES.items():
        try:
            print(f"Fetching {source_name}...", end=" ")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"❌ (empty)")
                broken_sources.append(source_name)
                continue
            
            print(f"✓ ({len(feed.entries)} items)")
            working_sources.append(source_name)
            
            # Get ALL items without filtering
            for entry in feed.entries[:15]:
                title = entry.get('title', 'Untitled')
                link = entry.get('link', '')
                description = entry.get('summary', '')[:600]
                pubDate = entry.get('published', datetime.utcnow().isoformat())
                guid = entry.get('id', link if link else f"{source_name}-{title}")
                
                all_items.append({
                    'title': title,
                    'link': link,
                    'description': description,
                    'pubDate': pubDate,
                    'source': source_name,
                    'guid': guid
                })
        except Exception as e:
            print(f"❌ (Error: {str(e)[:30]})")
            broken_sources.append(source_name)
    
    print(f"\n{'='*50}")
    print(f"Total items collected: {len(all_items)}")
    print(f"Working sources: {len(working_sources)}/{len(SOURCES)}")
    print(f"Failed sources: {broken_sources}")
    print(f"{'='*50}\n")
    
    # Sort by date
    try:
        all_items.sort(key=lambda x: x['pubDate'], reverse=True)
    except:
        pass
    
    # Create RSS
    rss = Element('rss', {
        'version': '2.0',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = 'EU & Swiss News Feed'
    SubElement(channel, 'link').text = 'https://github.com'
    SubElement(channel, 'description').text = 'Latest news from Europe covering politics, economy, and security'
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    for item in all_items[:200]:
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
    
    print(f"✓ Feed saved with {len(all_items)} items from {len(working_sources)} sources")

if __name__ == '__main__':
    fetch_and_aggregate()
