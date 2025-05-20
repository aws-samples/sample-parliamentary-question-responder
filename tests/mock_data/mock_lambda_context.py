class LambdaContext:
	def __init__(self, context = {}):
		self.function_name = context.get('function_name', 'test-function')
		self.function_version = context.get('function_version', '1.0')
		self.invoked_function_arn = context.get('invoked_function_arn', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
		self.memory_limit_in_mb = context.get('memory_limit_in_mb', 128)
		self.aws_request_id = context.get('aws_request_id', 'test-request-id')
		self.log_group_name = context.get('log_group_name', 'test-log-group')
		self.log_stream_name = context.get('log_stream_name', 'test-log-stream')
