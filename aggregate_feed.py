#!/usr/bin/env python3
import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# VERIFIED WORKING FEEDS - Economy, Politics, Security
SOURCES = {
    # ===== TOP-TIER NEWS =====
    'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
    'Reuters World': 'https://feeds.reuters.com/reuters/worldNews',
    'AP News Europe': 'https://apnews.com/apf-services/APNewsFeeds?category=world&subcategory=europe&outputType=rss',
    'BBC Europe': 'http://feeds.bbc.co.uk/news/world/europe/rss.xml',
    'BBC World': 'http://feeds.bbc.co.uk/news/world/rss.xml',
    
    # ===== PREMIUM POLITICAL ANALYSIS =====
    'Politico Europe': 'https://www.politico.eu/feed/',
    'Euractiv': 'https://www.euractiv.com/feed/',
    'DW Europe': 'https://rss.dw.com/xml/rss-en-eu',
    'DW Top Stories': 'https://rss.dw.com/xml/rss-en-top',
    'ECFR (Foreign Relations)': 'https://ecfr.eu/feed/',
    
    # ===== SWISS PREMIUM =====
    'NZZ': 'https://www.nzz.ch/feed',
    'Tages-Anzeiger': 'https://www.tagesanzeiger.ch/feed',
    'SRF News': 'https://www.srf.ch/news/bnews/rss/2c835f36-c934-4e31-aa35-08732e97af5e',
    'Swissinfo': 'https://www.swissinfo.ch/feed/rss/latest',
    
    # ===== BUSINESS & ECONOMICS =====
    'Financial Times World': 'https://www.ft.com/?format=rss',
    'CNBC International': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
    'Bloomberg Europe': 'https://www.bloomberg.com/feed/podcast/etf-report.xml',
    
    # ===== SECURITY & GEOPOLITICS =====
    'RFE/RL Europe': 'https://www.rferl.org/feed/europe-report/24259.xml',
    'Stratfor Geopolitical Intelligence': 'https://feeds.stratfor.com/stratfor/geopolitical-diary',
    'War on the Rocks': 'https://warontherocks.com/feed/',
    
    # ===== EU POLICY & GOVERNANCE =====
    'EU Observer': 'https://euobserver.com/feed',
    'Brussel.Blog': 'https://brussels.blog/feed/',
    'Politico Pro': 'https://www.politico.eu/feed/',
    
    # ===== ENERGY & CLIMATE POLICY =====
    'Carbon Brief': 'https://www.carbonbrief.org/feed/',
    'Energy Post': 'https://energypost.eu/feed/',
    
    # ===== TRADE & COMMERCE =====
    'World Economic Forum': 'https://www.weforum.org/feed.rss',
    'Trade Finance Global': 'https://www.tradefinanceglobal.com/feed/',
    
    # ===== REGULATORY & COMPLIANCE =====
    'Reuters Legal': 'https://feeds.reuters.com/reuters/businessNews',
    'European Law Blog': 'https://europeanlawblog.eu/feed/',
}

def fetch_and_aggregate():
    all_items = []
    successful_sources = []
    failed_sources = []
    
    for source_name, feed_url in SOURCES.items():
        try:
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                print(f"⚠️  {source_name}: No items (feed may be empty)")
                failed_sources.append(source_name)
                continue
            
            successful_sources.append(source_name)
            
            # Get top items from each source
            for entry in feed.entries[:10]:
                title = entry.get('title', 'Untitled')
                
                # Topic filtering
                relevant_keywords = [
                    # Economy
                    'economy', 'economic', 'trade', 'tariff', 'inflation', 'gdp', 'interest rate',
                    'monetary', 'fiscal', 'investment', 'market', 'finance', 'bank', 'euro',
                    'currency', 'export', 'import', 'commerce', 'supply chain', 'tax', 'customs',
                    'commerce', 'business', 'energy', 'oil', 'gas', 'commodity', 'inflation',
                    
                    # Politics
                    'politics', 'political', 'parliament', 'government', 'election', 'policy',
                    'regulation', 'law', 'agreement', 'summit', 'negotiation', 'treaty',
                    'european union', 'eu', 'swiss', 'switzerland', 'legislation', 'directive',
                    'council', 'commission', 'diplomat', 'minister', 'chancellor', 'president',
                    
                    # Security & Defense
                    'security', 'defense', 'military', 'nato', 'ukraine', 'russia',
                    'conflict', 'crisis', 'cyber', 'terrorism', 'intelligence',
                    'sanction', 'arms', 'war', 'peace', 'strategic', 'geopolitical',
                    'border', 'alliance', 'deterrence', 'strengthen', 'threat',
                ]
                
                title_lower = title.lower()
                is_relevant = any(keyword in title_lower for keyword in relevant_keywords)
                
                if is_relevant:
                    all_items.append({
                        'title': title,
                        'link': entry.get('link', ''),
                        'description': entry.get('summary', '')[:600],
                        'pubDate': entry.get('published', datetime.utcnow().isoformat()),
                        'source': source_name,
                        'guid': entry.get('id', entry.get('link', f"{source_name}-{title}"))
                    })
        except Exception as e:
            print(f"✗ {source_name}: {str(e)[:50]}")
            failed_sources.append(source_name)
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
    SubElement(channel, 'title').text = 'Premium EU & Swiss News - Economy, Politics, Security'
    SubElement(channel, 'link').text = 'https://github.com'
    SubElement(channel, 'description').text = 'Curated from Reuters, Politico, DW, BBC, Financial Times, and other top sources covering economy, politics, and security'
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    for item in all_items[:150]:
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
    
    print(f"\n✓ Feed generated successfully!")
    print(f"  Total items: {len(all_items)}")
    print(f"  Working sources: {len(successful_sources)}/{len(SOURCES)}")
    print(f"  Failed/Empty: {len(failed_sources)}")

if __name__ == '__main__':
    fetch_and_aggregate()
