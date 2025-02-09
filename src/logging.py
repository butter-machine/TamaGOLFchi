"""Logging module."""

import os

ERROR = "Error"
WARNING = "Warning"
INFO = "Info"
DEBUG = "Debug"
EXCEPTION = "Exception"
PRIORITY = {	# Lower -> More prioritized.
    EXCEPTION: 0,
    ERROR: 1,
    WARNING: 2,
    INFO: 3,
    DEBUG: 4,
}
    

class Logger:
    """
    A simple logger that prints messages in serial and (optionally) in file.
    
    To handle exceptions use context manager functionality, for example:
    with Logger(INFO, "/test.log") as logger:
        raise RuntimeError("A test exception occurred!")
    """
    
    @staticmethod
    def _init_log_file(log_file_path: str):
        """Create if not exists and open."""
        if log_file_path:
            return open(log_file_path, "a")
        return
    
    def __init__(self, verbosity: str = INFO, log_file_path: str = None):
        """
        Initialize logger with:
        - verbosity: One of ERROR, WARNING, INFO, DEBUG, EXCEPTION, default is INFO.
        - log_file_path: a path of a file to write files into - if exists, new logs will be appended.
        """
        self.log_file_path = log_file_path
        self.log_file = self._init_log_file(self.log_file_path)
        self.verbosity = verbosity
    
    @staticmethod
    def _format_message(verbosity: str, message: str) -> str:
        """Format message like: `[INFO]: Cool message.`"""
        return "[{verbosity}]: {message}".format(
            verbosity=verbosity,
            message=message,
        )
    
    def _handle(self, verbosity: str, message: str):
        """Handle logging if under verbosity by printing into serial and optionally in the file."""
        if PRIORITY[verbosity] > PRIORITY[self.verbosity]:
            return
        formatted_message = self._format_message(verbosity, message)
        print(formatted_message)
        if self.log_file:
            self.log_file.write(formatted_message + "\n")
            self.log_file.flush()	# Ensure the data is written to the file
    
    def error(self, message: str):
        """Log with ERROR verbosity."""
        verbosity = ERROR
        self._handle(verbosity, message)
        
    def warning(self, message: str):
        """Log with WARNING verbosity."""
        verbosity = WARNING
        self._handle(verbosity, message)
    
    def info(self, message: str):
        """Log with INFO verbosity."""
        verbosity = INFO
        self._handle(verbosity, message)
        
    def debug(self, message: str):
        """Log with DEBUG verbosity."""
        verbosity = DEBUG
        self._handle(verbosity, message)
        
    def __enter__(self):
        """Enter context manager returning self."""
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        """Exit context manager logging exceptions and re-raising the original one."""
        if exc_type is not None:
            import io
            import sys
            trace_buffer = io.StringIO()
            sys.print_exception(exc_value, trace_buffer)
            trace_content = trace_buffer.getvalue()
            self._handle(EXCEPTION, f"Traceback:\n{trace_content}")
        
        if self.log_file:
            self.log_file.close()
        
        return False	# Allow the exception to propagate
