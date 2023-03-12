import requests
import unicodedata
from configparser import ConfigParser


def address_generator(item) -> str:
    res = []
    for i in item['adm_div']:
        if i['type'] in ('district', 'living_area'):
            res.append(unicodedata.normalize('NFKD', i['name']))

    res = ', '.join(res) if len(res) > 1 else ''.join(res)
    return f"{res}, {item['name']}"


class DGis:
    def __init__(self, cfg_path):
        parser = ConfigParser()
        if parser.read(cfg_path):
            self.key = parser['2GIS']['KEY']
            self.fields = parser['2GIS']['FIELDS']
            self.city_id = parser['2GIS']['CITY_ID']
        else:
            raise FileNotFoundError(f'Config file {cfg_path} not found')

        self.url = 'https://catalog.api.2gis.com/3.0/items/geocode'

    def get_info(self, query):
        try:
            response = requests.get(self.url,
                                    params={'q': query,
                                            'fields': self.fields,
                                            'city_id': self.city_id,
                                            'key': self.key,
                                            'search_is_query_text_complete': 'true'
                                            })

            if response.json()['meta']['code'] == 200:
                item = response.json()['result']['items'][0]

                return {'point': (str(item['point']['lat']), str(item['point']['lon'])),
                        'address': address_generator(item)}
            else:
                print(response.json()['meta']['error']['message'])
                return None

        except requests.exceptions.RequestException as e:
            print('Exception occurred.', e)
            return None


if __name__ == '__main__':
    gis = DGis('data/dgis.cfg')
    resp = gis.get_info('улица абубекира дом 42 ')
    print(resp)
