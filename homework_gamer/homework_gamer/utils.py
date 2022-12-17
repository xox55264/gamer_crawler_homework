import re
import os
import hashlib
import redis
from time import time
from datetime import datetime, timedelta, date

class Helper:

    @staticmethod
    def current_time() -> str:
        return int(time()*1000)
        # return str(pytz.timezone('Asia/Taipei').localize(datetime.now()).isoformat())

    @staticmethod
    def clear_content(content: str) -> str:
        return re.sub(r'\s+', '', content).replace('"', '').replace("'", '')\
            .replace(u'\u200b', '').replace(u'\u009f', '')

    @staticmethod
    def get_config(name: str) -> dict:
        if os.environ['ENVIRONMENT'] == 'LOCAL':
            log_path = '{f}/{n}.log'.format(f=os.environ['SPIDER_LOG_PATH'], n=name)
            data_path = '{f}/{n}_{t}.jl'.format(f=os.environ['SPIDER_DATA_PATH'], n=name, t=datetime.now().strftime('%Y%m%d%H%M%S'))
            return {'LOG_FILE':log_path, 'FEED_URI':data_path}
        else:
            return {}

    @staticmethod
    def sha1_encode(encode_target: str) -> str:
        return hashlib.sha1(encode_target).hexdigest()

    @staticmethod
    def sha256_encode(encode_target: str) -> str:
        return hashlib.sha256(encode_target).hexdigest()

    @staticmethod
    def get_datetime_range(month, year=0):
        target_date = [{'year': datetime.now().year,
                        'month': datetime.now().month}]

        for i in range(0, month):
            last = date(target_date[i]['year'],target_date[i]['month'],1) - timedelta(days=1)
            target_date.append({'year': last.year, 'month': last.month})

        return target_date



class RedisHelper(object):
    """docstring for RedisHelper"""
    # def __init__(self):
    #     super(RedisHelper, self).__init__()
    #     self.r = redis.Redis(host=os.environ['REDIS_HOST'],
    #                          port=int(os.environ['REDIS_PORT']),
    #                          password=os.environ['REDIS_AUTH'],
    #                          decode_responses=True)
    # def __init__(self):
    #     super(RedisHelper, self).__init__()
    #     self.r = redis.Redis(host='127.0.0.1',
    #                          port=6379,
    #                          decode_responses=True)

    def __init__(self):
        super(RedisHelper, self).__init__()
        self.r = redis.Redis(host='docker.for.mac.host.internal',
                             port=6379,
                             decode_responses=True)

    def get_value(self, key):
        return self.r.get(key)

    def set_value(self, key, value, expire=None):
        return self.r.set(key, value, ex=expire, nx=True)

    def compare_vaule(self, key, value):
        return value == self.get_value(key)

    def delete_key(self, key):
        return self.r.delete(key)

    def check_key_exist(self, key):
        return self.r.exists(key)

    def check_spider_exist(self, spider_name):
        exist = self.check_key_exist(f'spider_{spider_name}')
        if not exist:
            self.set_value(key=f'spider_{spider_name}', value='', expire=86400)
        return exist

    def remove_spider_key(self, spider_name):
        return self.delete_key(f'spider_{spider_name}')