from kombu import Exchange, Queue

from ..common.constants import RABBIT_HOST

broker_url = f"pyamqp://guest@{RABBIT_HOST}//"
task_serializer = 'json'
accept_content = ['json']

task_routes = {
    'register_result': {'queue': 'results'},
    'update_current_jobs': {'queue': 'backend'},
    'convert_to_latex': {'queue': 'backend'},
    'register_subtask_completion': {'queue': 'backend'},
    'register_subtask_status': {'queue': 'backend'},
    'build_latex': {'queue': 'latex_builder_queue'},
}
task_queues = (
    Queue('results', Exchange('backend_results'), routing_key='results'),
    Queue('backend', Exchange('backend'), routing_key='backend'),
    Queue('latex_builder_queue', Exchange('latex_builder'), routing_key='latex_builder_queue'),
)
