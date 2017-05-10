########################################################################
# logger.py -- log in a common format to a file.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin Mosbeck    <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import logging
import os

class AutosubLogger(threading.Thread):
    """
    Logger thread for autosub.
    """

    def __init__(self, name, logger_queue, log_dir, log_threshhold):
        """
        Constructor for logger thread.
        """

        threading.Thread.__init__(self)
        self.name = name
        self.logger_queue = logger_queue
        self.log_dir = log_dir
        self.format_autosub = "%(asctime)-15s [%(log_src)-12s] %(levelname)s: %(log_msg)s"
        self.format_tasks = 80 * '-' + "\n%(asctime)-15s [%(log_src)-12s]%(levelname)s:\n" \
                            + 80 * '-' + "\n%(log_msg)s"
        self.loggers_info = {"autosub":    ["autosub.log", self.format_autosub],\
                             "task_msg":   ["tasks.stdout", self.format_tasks],\
                             "task_error": ["tasks.stderr", self.format_tasks]}
        self.loggers = dict()

        if log_threshhold == 'DEBUG':
            self.log_threshhold = logging.DEBUG
        elif log_threshhold == 'INFO':
            self.log_threshhold = logging.INFO
        elif log_threshhold == 'WARNING':
            self.log_threshhold = logging.WARNING
        elif log_threshhold == 'ERROR':
            self.log_threshhold = logging.ERROR

    def setup_logger(self, logger_name, logger_info):
        """
        Set up a logger with own log file.
        """

        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_threshhold)
        formatter = logging.Formatter(logger_info[1])
        file_handler = logging.FileHandler(self.log_dir + "/" + logger_info[0])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def run(self):
        """
        Thread main code.
        """

        # create log_dir if necessary
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        # create loggers
        for logger_name, logger_info in self.loggers_info.items():
            self.loggers[logger_name] = self.setup_logger(logger_name, logger_info)

        while True:
            next_log_msg = self.logger_queue.get(True)
            log_dst = str(next_log_msg.get("log_dst"))
            log_src = str(next_log_msg.get('log_src'))
            log_msg = str(next_log_msg.get('msg'))
            log_level = str(next_log_msg.get('type'))

            d = dict({"log_src": log_src, "log_msg": log_msg})

            if log_level == "DEBUG":
                self.loggers[log_dst].debug("%s ", extra=d)
            elif log_level == "INFO":
                self.loggers[log_dst].info("%s ", extra=d)
            elif log_level == "WARNING":
                self.loggers[log_dst].warning("%s ", extra=d)
            elif log_level == "ERROR":
                self.loggers[log_dst].error("%s ", extra=d)

            # if we don't know, we assume the worst
            else:
                self.loggers[log_dst].error("%s ", extra=d)
