from kombu import Exchange, Queue

from ..common.constants import RABBIT_HOST

broker_url = f"pyamqp://guest@{RABBIT_HOST}//"
task_serializer = 'json'
accept_content = ['json']

task_routes = {
    'register_result': {'queue': 'results'}
}
task_queues = (
    Queue('results', Exchange('backend_results'), routing_key='results'),
)
