import re
import requests
import time
from pymongo import MongoClient
from bson import ObjectId
import pymongo
from tqdm import tqdm

client = MongoClient("mongodb+srv://mongo_db_admin:Qqwerty123456@cluster0.fvfnv.mongodb.net/<dbname>?retryWrites=true&w=majority")

class Users:
    _params = {
        'offset': 0,
        'age': '',
        'sex': 0,
        'city': 0,
        'status': ''
    }

    def __init__(self, token, age, sex, city, status=None):
        self.token = token
        self.age = age
        self.sex = sex
        self.city = city
        self.status = status

    def get_params(self):
        return {
            'access_token': self.token,
            'city': self.get_cities(),
            'age_from': self.age,
            'age_to': self.age,
            'status': self.status,
            'sex': self.define_sex(),
            'count': 10,
            'v': '5.89'
        }

    def get_cities(self):       # Определяем идендификатор города
        params = {
            'access_token': self.token,
            'country_id': 1,
            'q': self.city,
            'v': '5.21'
        }
        response = requests.get('https://api.vk.com/method/database.getCities', params=params)
        response = response.json()['response']['items'][0]['id']
        return response

    def define_sex(self):
        pattern_female = re.compile(r'^[ж|Ж]\D+')
        pattern_male = re.compile(r'^[м|М]\D+')
        if re.match(pattern_female, self.sex) != None:
            return 1
        elif re.match(pattern_male, self.sex) != None:
            return 2
        else:
            return 0

    def get_users(self):     # Получить список пользователей по параметрам
        offset = 0
        params = self.get_params()
        if (params['city'] == self._params['city']) and (params['sex'] == self._params['sex']) and (params['age_to'] == self._params['age']) and (params['status'] == self._params['status']):
            offset = self._params['offset']
        else: pass
        params['offset'] = offset
        response = requests.get('https://api.vk.com/method/users.search', params=params)
        response = response.json()['response']['items']
        id_list = []
        for user_data in response:
            id_list.append(user_data['id'])
        new_offset = offset + 10
        self._params['offset'] = new_offset
        self._params['age'] = params['age_to']
        self._params['sex'] = params['sex']
        self._params['city'] = params['city']
        self._params['status'] = params['status']
        return id_list

    def get_photos(self): # Получить фотографии пользователей
        params = {
            'access_token': self.token,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'v': '5.77'
        }
        top_photos = []
        for user in tqdm(self.get_users()):
            profile_photos = []
            params['owner_id'] = user
            try:
                time.sleep(0.5)
                response = requests.get('https://api.vk.com/method/photos.get', params=params)
                response = response.json()
                if response['response']['count'] != 0:
                    for data in response['response']['items']:
                        result = {
                            'owner_id': 0,
                            'url': '',
                            'likes': 0
                        }
                        sorted_photos_url = sorted(data['sizes'], key = lambda x: (x['type']), reverse=True)
                        result['owner_id'] = data['owner_id']
                        result['likes'] = data['likes']['count']
                        result['url'] = sorted_photos_url[0]['url']
                        profile_photos.append(result)
                else: continue
            except KeyError:
                continue
            profile_photos = sorted(profile_photos, key = lambda x: (x['likes']), reverse=True)
            profile_photos = profile_photos[0:3]
            result = {
                'profile_url': f'https://vk.com/id{profile_photos[0]["owner_id"]}',
                'photo_url':[]
            }
            for photo_info in profile_photos:
                result['photo_url'].append(photo_info['url'])
            top_photos.append(result)
        return top_photos


if __name__ == "__main__":
    while True:
        token = input('Введите TOKEN для успешной аутентификации: ')
        age = input('Укажите возраст для поиска подходящей пары: ')
        sex = input('Укажите пол мужчина/женьщина или оставьте поле пустым для снятия оганичений: ')
        city = input('Укажите город для поиска: ')
        status = input('''
            Укажите семейное положение (цифровое значение):
            1 - не женат (не замужем);
            2 - встречается;
            3 - помолвлен(-а);
            4 - женат (замужем);
            5 - всё сложно;
            6 - в активном поиске;
            7 - влюблен(-а);
            8 - в гражданском браке.
        ''')
        User = Users(token, age, sex, city, status)
        users_db = client['users_db']
        users_collection = users_db['collection']
        for item in User.get_photos():
            users_collection.insert_one(item).inserted_id
        