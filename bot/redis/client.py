import redis

class RedisClient:

    def __init__(self, config):
        host = config['host']
        port = config['port']
        password = config['password']
        self.client = redis.Redis(host=host, port=port, password=password, decode_responses=True)

    def increment_sorted_set(self, set_name, user_id, amount_to_increment):
        try:
            return int(self.client.zincrby(set_name, amount_to_increment, user_id))
        except Exception as e:
            print(e)