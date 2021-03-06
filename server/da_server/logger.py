import logging

from da_server import api

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


class JSONHandler(logging.Handler):
    """
    Logging handler that sends logs as JSONs
    """
    def __init__(self, communication_handler, run_id):
        """
        Initialize the instance with the communication handler
        """
        logging.Handler.__init__(self)
        self.communication_handler = communication_handler
        self.run_id = run_id


    def map_log_record(self, record):
        """
        Mapping the log record into a dict to send
        """
        return api.APISerializer.serialize_log(level=record.levelname,
                                               message=record.msg,
                                               run_id=self.run_id)

    def emit(self, record):
        """
        Emit a record.

        Send the record to the communication handler
        """
        self.communication_handler.send_json(self.map_log_record(record))
