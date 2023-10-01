from kombu import Exchange, Queue

from ..common.constants import RABBIT_HOST

broker_url = f"pyamqp://guest@{RABBIT_HOST}//"
task_serializer = 'json'
accept_content = ['json']

task_routes = {
    'register': {'queue': 'compressing_queue'}
}
task_queues = (
    Queue('compressing_queue', Exchange('default'), routing_key='compression'),
)
