redis_port = 6381
broker_url = 'redis://localhost:'+redis_port.__str__()+'/'
result_backend = 'redis'
task_track_started = True
