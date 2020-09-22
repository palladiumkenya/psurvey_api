from celery import task
from celery import shared_task


# We can have either registered task
# @task(name='summary')
# def send_import_summary():
#     print('Registered')
#     return 'i am there'

# Magic happens here ...
# or
# @shared_task
# def send_notifiction():
#     print('Here I\’m')
#     return 'i am here'
#     # Another trick
