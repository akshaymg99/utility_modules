import redis
from redis import Redis
#from redisbloom import Client
import time
from datetime import datetime


class ImageFilter_RCuckoo:
    # Uses cuckoo filter
    def __init__(self):
        self.db = Redis(host='localhost', port=6379, db=0)
        self.bloom = Client(host='localhost', port=6379)
        self.bloom.cfReserve('filter', 0.1, 1000)

    def add_to_filter(self, key, date, model):
        if not self.bloom.execute_command('CF.ADD', 'filter', key):
            self.db.hset(key, 'date', date)
            self.db.hset(key, 'model', model)
            self.db.zadd(model, {key: float(date)})
            return False
        return True

    def check_in_filter(self, key):
        return self.bloom.execute_command('CF.EXISTS', 'filter', key)

    def get_by_date_and_model(self, model, start_date, end_date):
        keys_in_range = self.db.zrangebyscore(model, start_date, end_date)
        return [(key, self.db.hget(key, 'date')) for key in keys_in_range]

    def delete_from_filter(self, key):
        if self.bloom.execute_command('CF.DEL', 'filter', key):
            model = self.db.hget(key, 'model')
            self.db.zrem(model, key)
            self.db.delete(key)
            return True
        return False



class ImageFilter_RBloom:
    def __init__(self):
        self.client = Client(host='localhost', port=6379, db=0)

    def add_embedding(self, thumbnail, modelname, date):
        key = f"{thumbnail}_{modelname}"
        self.client.bfAdd('embedding_filter', key)
        self.client.hset(key, 'last_written_date', date)
        self.client.zadd('embedding_dates', {key: date})
        self.client.zadd(f'embedding_model_{modelname}', {key: date})

    def exists_embedding(self, thumbnail, modelname):
        key = f"{thumbnail}_{modelname}"
        return self.client.bfExists('embedding_filter', key) and self.client.hexists(key, 'last_written_date')

    def get_last_written_date(self, thumbnail, modelname):
        key = f"{thumbnail}_{modelname}"
        return self.client.hget(key, 'last_written_date')

    def delete_embedding(self, thumbnail, modelname):
        key = f"{thumbnail}_{modelname}"
        self.client.delete(key)
        #self.client.bfDel('embedding_filter', key)
        self.client.zrem('embedding_dates', key)
        self.client.zrem(f'embedding_model_{modelname}', key)

    def get_thumbnail_by_date_range(self, modelname, start_date, end_date):
        return self.client.zrangebyscore(f'embedding_model_{modelname}', start_date, end_date)

    def exists_modelname_in_filter(self, modelname):
        return self.client.exists(f'embedding_model_{modelname}')


class ImageFilter_Rhash:
    # redis hash-key implementation
    def __init__(self):
        self.redis_db = redis.Redis()

    def insert(self, thumbnail, modelname):
        key = f'{thumbnail}_{modelname}'
        #now_time = datetime.now()
        #last_written_date = now_time.strftime("%m/%d/%Y, %H:%M:%S")
        last_written_date = int(time.time())
        # Store the metadata in a hash
        self.redis_db.hset(key, 'last_written_date', last_written_date)
        # Add to sorted set
        self.redis_db.zadd('thumbnails', {key: last_written_date})   # TODO: 120 is a dummy value, replace with actual date

    def exists(self, thumbnail, modelname):
        key = f'{thumbnail}_{modelname}'
        return self.redis_db.exists(key)

    def get_last_written_date(self, thumbnail, modelname):
        key = f'{thumbnail}_{modelname}'
        if not self.redis_db.exists(key):
            return None
        return int(self.redis_db.hget(key, 'last_written_date'))

    # Given range of date, which are the keys present in db?
    def get_keys_by_date_range(self, start_date, end_date):
        thumbnail_lst = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
        return [thumbnail.decode('utf-8') for thumbnail in thumbnail_lst]

    # Given modelname, & range of date, which are the thumbnails present in db?
    def get_thumbnail_by_date_range(self, start_date, end_date, modelname=None):
        if modelname is None:
            # return all thumbnails in db
            keys_res = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
        else:
            keys_all = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
            modelname_bytes = modelname.encode('utf-8')
            keys_res = [key for key in keys_all if key.endswith(b'_' + modelname_bytes)]  # Filter keys to include only those that end with the given modelname
        thumbnails = [key.decode('utf-8').split('_')[0] for key in keys_res]    # Extract the thumbnails from the keys
        return thumbnails

    # Given thumbnail, & range of date, which are the models present in solr?
    def get_modelname_by_date_range(self, start_date, end_date, thumbnail=None):
        if thumbnail is None:
            # return all modelnames in db
            keys_res = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
        else:
            keys_all = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
            thumbnail_bytes = thumbnail.encode('utf-8')
            keys_res = [key for key in keys_all if key.startswith(thumbnail_bytes + b'_')]
        modelnames = [key.decode('utf-8').split('_')[1] for key in keys_res]
        return modelnames

    def delete_by_thumbnail(self, thumbnail):
        keys = self.redis_db.keys(f'{thumbnail}_*')
        self.redis_db.delete(*keys)
        self.redis_db.zrem('thumbnails', *keys)

    def delete_by_modelname(self, modelname):
        keys = self.redis_db.keys(f'*_{modelname}')
        self.redis_db.delete(*keys)
        self.redis_db.zrem('thumbnails', *keys)

    def delete_by_date_range(self, start_date, end_date):
        keys = self.redis_db.zrangebyscore('thumbnails', start_date, end_date)
        self.redis_db.delete(*keys)
        self.redis_db.zrem('thumbnails', *keys)

    def delete(self, thumbnail=None, modelname=None):
        if thumbnail is None and modelname is None:
            raise Exception("Either thumbnail or modelname must be provided")
        elif thumbnail is None:
            self.delete_by_modelname(modelname)
        elif modelname is None:
            self.delete_by_thumbnail(thumbnail)
        else:
            key = f'{thumbnail}_{modelname}'
            self.redis_db.delete(key)
            self.redis_db.zrem('thumbnails', key)


if __name__ == "__main__":

    image_filter = ImageFilter_Rhash()
    thumbnail = 'thumbnailxyz'
    modelname = 'somemodel'
    #image_filter.insert(thumbnail, modelname)
    print(image_filter.exists(thumbnail, modelname))
    print(image_filter.get_last_written_date(thumbnail, modelname))
    print(image_filter.get_keys_by_date_range(0, 1685466720))
    print(image_filter.get_thumbnail_by_date_range(0, 1685466720, modelname=modelname))
    print(image_filter.get_thumbnail_by_date_range(0, 1685466720))
    print(image_filter.get_modelname_by_date_range(0, 1685466720, thumbnail=thumbnail))
    print(image_filter.get_modelname_by_date_range(0, 1685466720))

    #image_filter.delete(thumbnail, modelname)
    #print(image_filter.exists(thumbnail, modelname))




