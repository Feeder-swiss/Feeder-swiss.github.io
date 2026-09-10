#!/usr/bin/env python3
import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

# Premium institutional + news sources - Economy, Politics, Security
SOURCES = {
    # ===== ECONOMIC INSTITUTIONS =====
    'European Central Bank (ECB)': 'https://www.ecb.europa.eu/rss/press.html',
    'ECB Economic Bulletin': 'https://www.ecb.europa.eu/rss/econbull.html',
    'IMF News': 'https://www.imf.org/external/rss/news.xml',
    'World Bank': 'https://www.worldbank.org/en/rss/all',
    'European Investment Bank': 'https://www.eib.org/en/rss',
    'European Commission Economy': 'https://ec.europa.eu/commission/news/rss-feeds_en',
    
    # ===== SECURITY & DEFENSE =====
    'NATO Official': 'https://www.nato.int/nato_static_fl2014/assets/rss_feeds/news_en.xml',
    'EU External Action': 'https://eeas.europa.eu/headquarters/rss_en.xml',
    'European Council': 'https://www.consilium.europa.eu/en/rss/',
    'European Defence Agency': 'https://www.eda.europa.eu/en/newsroom/rss',
    
    # ===== POLITICAL INSTITUTIONS =====
    'European Parliament News': 'https://www.europarl.europa.eu/news/en/headlines/rss',
    'Council of EU Presidency': 'https://www.consilium.europa.eu/en/rss/',
    'Swiss Parliament (Federal Assembly)': 'https://www.parlament.ch/en/web-services/rss',
    
    # ===== TOP-TIER NEWS - ECONOMY, POLITICS, SECURITY =====
    'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
    'Reuters Politics': 'https://feeds.reuters.com/reuters/worldNews',
    'Reuters Security': 'https://feeds.reuters.com/reuters/worldNews',
    'AP News Europe': 'https://apnews.com/apf-services/APNewsFeeds?category=world&subcategory=europe&outputType=rss',
    'BBC Europe': 'http://feeds.bbc.co.uk/news/world/europe/rss.xml',
    
    # ===== PREMIUM ANALYSIS - EU & SWISS POLITICS =====
    'Politico Europe': 'https://www.politico.eu/feed/',
    'Euractiv': 'https://www.euractiv.com/feed/',
    'ECFR (European Council on Foreign Relations)': 'https://ecfr.eu/feed/',
    'DW Europe': 'https://rss.dw.com/xml/rss-en-eu',
    'DW Europe News': 'https://rss.dw.com/xml/rss-en-top',
    
    # ===== SWISS PREMIUM SOURCES =====
    'NZZ (Politics & Economy)': 'https://www.nzz.ch/feed',
    'Tages-Anzeiger': 'https://www.tagesanzeiger.ch/feed',
    'SRF News': 'https://www.srf.ch/news/bnews/rss/2c835f36-c934-4e31-aa35-08732e97af5e',
    'Swissinfo.ch': 'https://www.swissinfo.ch/feed/rss/latest',
    
    # ===== SPECIALIZED POLICY & TRADE =====
    'WTO News': 'https://www.wto.org/english/news_e/rss_e/feed_en.rss',
    'OECD': 'https://oecdobserver.wordpress.com/feed/',
    'Financial Times Europe': 'https://markets.ft.com/data',
    'The Economist Europe': 'https://www.economist.com/europe/rss.xml',
    
    # ===== COMPLIANCE & REGULATION =====
    'European Banking Authority': 'https://www.eba.europa.eu/rss-feeds',
    'European Securities and Markets Authority': 'https://www.esma.europa.eu/rss',
}

def fetch_and_aggregate():
    all_items = []
    
    for source_name, feed_url in SOURCES.items():
        try:
            feed = feedparser.parse(feed_url)
            # Get top items from each source
            for entry in feed.entries[:10]:
                # Extract item data
                title = entry.get('title', 'Untitled')
                
                # Topic filtering - catches economy, politics, security keywords
                relevant_keywords = [
                    # Economy
                    'economy', 'economic', 'trade', 'tariff', 'inflation', 'gdp', 'interest rate',
                    'monetary', 'fiscal', 'ecb', 'imf', 'world bank', 'investment', 'market',
                    'finance', 'bank', 'euro', 'currency', 'export', 'import', 'commerce',
                    'supply chain', 'debt', 'deficit', 'revenue', 'tax', 'customs',
                    
                    # Politics
                    'politics', 'political', 'parliament', 'government', 'election', 'policy',
                    'regulation', 'law', 'agreement', 'summit', 'negotiation', 'treaty',
                    'european union', 'eu', 'swiss', 'switzerland', 'legislation', 'directive',
                    'council', 'commission', 'parliament', 'congress', 'diplomat',
                    
                    # Security & Defense
                    'security', 'defense', 'defense', 'military', 'nato', 'ukraine', 'russia',
                    'conflict', 'crisis', 'crisis', 'cyber', 'terrorism', 'intelligence',
                    'sanction', 'arms', 'war', 'peace', 'strategic', 'geopolitical',
                    'border', 'alliance', 'deterrence', 'strengthen',
                    
                    # Institutions & Authority
                    'ecb', 'imf', 'nato', 'eba', 'esma', 'wto', 'oecd', 'eib',
                    'central bank', 'federal reserve', 'regulatory', 'authority'
                ]
                
                title_lower = title.lower()
                is_relevant = any(keyword in title_lower for keyword in relevant_keywords)
                
                # Include if relevant (or from institutional sources, include all)
                if is_relevant or 'ECB' in source_name or 'IMF' in source_name or 'NATO' in source_name or 'Parliament' in source_name or 'Commission' in source_name or 'Council' in source_name or 'Authority' in source_name:
                    all_items.append({
                        'title': title,
                        'link': entry.get('link', ''),
                        'description': entry.get('summary', '')[:600],
                        'pubDate': entry.get('published', datetime.utcnow().isoformat()),
                        'source': source_name,
                        'guid': entry.get('id', entry.get('link', f"{source_name}-{title}"))
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
    SubElement(channel, 'title').text = 'Premium EU & Swiss News - Economy, Politics, Security'
    SubElement(channel, 'link').text = 'https://github.com'
    SubElement(channel, 'description').text = 'Curated from ECB, IMF, NATO, EU institutions, and top-tier news sources covering economy, politics, and security'
    SubElement(channel, 'language').text = 'en-us'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    SubElement(channel, 'image/url').text = 'https://github.com'
    
    for item in all_items[:200]:  # Keep many items from diverse sources
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
    
    print(f"✓ Feed generated with {len(all_items)} items from {len(SOURCES)} premium sources")
    print(f"  Sources: ECB, IMF, NATO, World Bank, EU Institutions, Top-tier News")

if __name__ == '__main__':
    fetch_and_aggregate()
