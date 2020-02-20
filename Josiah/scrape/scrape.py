import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import itertools

response = requests.get("https://wikimapping.com/mapdata.php?z=10&cats=9280&other=1&min_x=-119.23049926757814&min_y=33.959308210392024&max_x=-117.25296020507812&max_y=34.120900139826965&clat=34.04014265821754&clng=-118.24172973632812&osm=1&ss_proj_id=1337&f=0")

places = json.loads(response.content.decode().replace('\n', '').replace('\t', '').replace('"', '').replace("'", '"').split('locations = ')[1].split(';plines')[0])
all_addcomments = []
data = []
print('I got', len(places), 'to do.')
for i, p in enumerate(places):
    html = requests.get(f"https://wikimapping.com/ajax.php?op=add-comment&type=point&feature={p['id']}&cat_id={p['cat']}").content
    parsed_html = BeautifulSoup(html, features="lxml")
    commentAndVote = parsed_html.body.find('div').find('p').contents
    comment, vote = commentAndVote[1].replace(' \xa0', ''), commentAndVote[5].replace('\xa0', '')
    addcomments = [c.contents[0] for c in parsed_html.find_all('div', attrs={'class': 'comment'})]
    adddates = [c.find('div').contents[0].replace('"', '') for c in parsed_html.find_all('div', attrs={'class': 'comment'})]
    addusers = [c.find('i').text for c in parsed_html.find_all('div', attrs={'class': 'comment'}) if c.find('i')]
    all_addcomments = all_addcomments + list(zip(itertools.repeat(p['id']), addcomments, adddates, addusers))
    row = [p['id'], p['lat'], p['lng'], comment, vote]
    data.append(row)
    print('Done with', i)
    if i % 20 == 0:
        pd.DataFrame(data, columns=['id', 'lat', 'lng', 'comment', 'vote']).to_csv('./locations.csv', index=False)
        pd.DataFrame(all_addcomments, columns=['id', 'comment', 'date', 'user']).to_csv('./comments.csv', index=False)

pd.DataFrame(data, columns=['id', 'lat', 'lng', 'comment', 'vote']).to_csv('./locations.csv', index=False)
pd.DataFrame(all_addcomments, columns=['id', 'comment', 'date', 'user']).to_csv('./comments.csv', index=False)
print('done')