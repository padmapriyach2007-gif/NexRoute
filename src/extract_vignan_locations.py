import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.easytourz.com/BT-EmabedTour/all/a0ccdb54f97e5369'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')

menu = soup.find('div', id='cssmenu')
sections = {}
all_items = []
if menu:
    for li in menu.find_all('li', class_='has-sub'):
        main_a = li.find('a')
        category = main_a.get_text(strip=True) if main_a else 'Unknown'
        sub_items = []
        sub_ul = li.find('ul')
        if sub_ul:
            for sub_li in sub_ul.find_all('li'):
                sub_a = sub_li.find('a')
                if sub_a:
                    loc_name = sub_a.get_text(strip=True)
                    nav_id = sub_a.get('data-navuniqueid', '')
                    pano_id = sub_a.get('data-npanoid', '')
                    item = {
                        'category': category,
                        'name': loc_name,
                        'nav_id': nav_id,
                        'pano_id': pano_id
                    }
                    sub_items.append(item)
                    all_items.append(item)
        sections[category] = sub_items

with open('vignan_tour_locations.json', 'w', encoding='utf-8') as f:
    json.dump({'total': len(all_items), 'sections': sections, 'all_items': all_items}, f, indent=2)

print(f"Extracted {len(all_items)} locations across {len(sections)} sections successfully!")
