
class ProcessingError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        if 'run_id' in kwargs:
            self.run_id = kwargs['run_id']

