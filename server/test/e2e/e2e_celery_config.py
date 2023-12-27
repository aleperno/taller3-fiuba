from kombu import Exchange, Queue

broker_url = f"pyamqp://guest@localhost//"
task_serializer = 'json'

task_routes = {
  'register_result': {'queue': 'e2e-results'},
  'update_current_jobs': {'queue': 'e2e-tasks'},
  'convert_to_latex': {'queue': 'e2e-tasks'},
}

task_queues = (
  Queue('e2e-results', Exchange('e2e-results'), routing_key='results'),
  Queue('e2e-tasks', Exchange('e2e-tasks'), routing_key='tasks'),
)
