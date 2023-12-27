from kombu import Exchange, Queue

broker_url = f"pyamqp://guest@localhost//"
task_serializer = 'json'

task_routes = {
  'register_result': {'queue': 'results'},
  'update_current_jobs': {'queue': 'tasks'},
  'convert_to_latex': {'queue': 'tasks'},
}

task_queues = (
  Queue('results', Exchange('results'), routing_key='results'),
  Queue('tasks', Exchange('tasks'), routing_key='tasks'),
)
