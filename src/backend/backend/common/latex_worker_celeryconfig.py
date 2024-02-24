from kombu import Exchange, Queue

from ..common.constants import RABBIT_HOST

broker_url = f"pyamqp://guest@{RABBIT_HOST}//"
task_serializer = 'json'
accept_content = ['json']

task_routes = {
    'build_latex': {'queue': 'latex_builder_queue'},
    'register_subtask_completion': {'queue': 'backend'},
}
task_queues = (
    Queue('backend', Exchange('backend'), routing_key='backend'),
    Queue('latex_builder_queue', Exchange('latex_builder'), routing_key='latex_builder_queue'),
)
