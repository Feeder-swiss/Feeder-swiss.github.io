#!/usr/bin/env python3
import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# Premium news sources - Economy, Politics, Security focus
SOURCES = {
    # Top-tier financial & economic analysis
    'Reuters Europe': 'https://feeds.reuters.com/reuters/businessNews',
    'Reuters Politics': 'https://feeds.reuters.com/reuters/worldNews',
    
    # Premium political analysis
    'Politico Europe': 'https://www.politico.eu/feed/',
    'Euractiv': 'https://www.euractiv.com/feed/',
    'DW Europe': 'https://rss.dw.com/xml/rss-en-eu',
    
    # Security & foreign policy
    'European Council on Foreign Relations': 'https://ecfr.eu/feed/',
    'DW Security': 'https://rss.dw.com/xml/rss-en-top',
    
    # Swiss premium sources
    'NZZ (Politics & Economy)': 'https://www.nzz.ch/feed',
    'Tages-Anzeiger': 'https://www.tagesanzeiger.ch/feed',
    'SRF News': 'https://www.srf.ch/news/bnews/rss/2c835f36-c934-4e31-aa35-08732e97af5e',
    'Swissinfo': 'https://www.swissinfo.ch/feed/rss/latest',
    
    # EU official sources
    'European Commission News': 'https://ec.europa.eu/commission/news/rss-feeds_en',
    'Council of the EU': 'https://www.consilium.europa.eu/en/rss/',
    
    # Specialized security & policy
    'BBC Europe': 'http://feeds.bbc.co.uk/news/world/europe/rss.xml',
    'AP News Europe': 'https://apnews.com/apf-services/APNewsFeeds?category=world&subcategory=europe&outputType=rss',
}

def fetch_and_aggregate():
    all_items = []
    
    for source_name, feed_url in SOURCES.items():
        try:
            feed = feedparser.parse(feed_url)
            # Get top items from each source
            for entry in feed.entries[:8]:
                # Extract item data
                title = entry.get('title', 'Untitled')
                
                # Basic filtering for relevant topics (optional - catches common keywords)
                relevant_keywords = ['economy', 'economic', 'trade', 'tariff', 'inflation', 'gdp', 
                                    'politics', 'political', 'parliament', 'government', 'election',
                                    'security', 'defense', 'military', 'nato', 'ukraine', 'russia',
                                    'policy', 'regulation', 'law', 'agreement', 'summit', 'crisis',
                                    'market', 'finance', 'investment', 'bank', 'eu', 'europe', 'swiss', 'switzerland']
                
                title_lower = title.lower()
                is_relevant = any(keyword in title_lower for keyword in relevant_keywords)
                
                # Include item if relevant (or if unsure, include it - better to have too much than too little)
                if is_relevant or len(title) > 0:
                    all_items.append({
                        'title': title,
                        'link': entry.get('link', ''),
                        'description': entry.get('summary', '')[:500],
                        'pubDate': entry.get('published', datetime.utcnow().isoformat()),
                        'source': source_name,
                        'guid': entry.get('id', entry.get('link', source_name))
                    })
        except Exception as e:
            print(f"⚠️  Error fetching {source_name}: {e}")
            continue
    
    # Sort by date (newest first)
    try:
        all_items.sort(key=lambda x: x['pubDate'], reverse=True)
    except:
        pass
    
    # Generate RSS
    rss = Element('rss', {
        'version': '2.0',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    
    channel = SubElement(rss, 'channel')
    SubElement(channel, 'title').text = 'EU & Swiss News - Economy, Politics, Security'
    SubElement(channel, 'link').text = 'https://github.com'
    SubElement(channel, 'description').text = 'Premium curated news on EU and Swiss economy, politics, and security from top international sources'
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    for item in all_items[:100]:  # Keep more items since filtered
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
    
    print(f"✓ Feed generated with {len(all_items)} relevant items from {len(SOURCES)} sources")

if __name__ == '__main__':
    fetch_and_aggregate()
