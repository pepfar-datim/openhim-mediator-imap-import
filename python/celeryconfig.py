redis_port = 6381
redis_host = 'localhost'
broker_url = 'redis://'+redis_host+':'+redis_port.__str__()+'/'
result_backend = 'redis'
