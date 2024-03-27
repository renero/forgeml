"""
This module contains the LogConfig class, which is used to configure logging 
for the pipeline.
"""

import logging
import time


class LogConfig:
    """
    Class to configure logging for the pipeline.
    """

    @staticmethod
    def setup_logging(
        name: str = None,
        level: str = "info",
        fname: str = None,
        caller_filename: str = None
    ):
        """
        Set up logging for the pipeline.

        Parameters:
        ------------
        - name (str): The name of the logger. Default is None.
        - fname (str): The name of the log file. Default is None.        
        - level (str): The level of logging to be used. Default is 'info'.
            Posible values are: 'debug', 'info', 'warning', 'error', 'critical'.
        - caller_filename (str): The name of the file that calls the logger. 
            Default is None.

        Returns:
        --------
        - logger: The logger object.
        """
        valid_levels = ['debug', 'info', 'warning', 'error', 'critical']
        assert level in valid_levels, \
            f"Level '{level}' not recognized. Possible values are: {valid_levels}"

        log_level = getattr(logging, level.upper())
        log_name = name if name is not None else \
            caller_filename.replace('.py', '')
        log_fname = fname if fname is not None else \
            f".{log_name}.log"

        tz = time.strftime('%z')
        fmt = '%(asctime)s' + tz + ' %(levelname)s %(message)s'
        logging.basicConfig(
            level=log_level,
            format=fmt,
            filename=log_fname,
            encoding="utf-8",
        )
        
        return logging.getLogger(log_name)
