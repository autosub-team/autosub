########################################################################
# logger.py -- log in a common format to a file.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin Mosbeck    <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import logging

class autosubLogger(threading.Thread):
    """
    Logger thread for autosub.
    """

    def __init__(self, thread_id, name, logger_queue, logfile):
        """
        Constructor for autosubLogger thread.
        """

        threading.Thread.__init__(self)
        self.name = name
        self.thread_id = thread_id
        self.logger_queue = logger_queue
        self.logfile = logfile

    def run(self):
        """
        Thread main code.
        """

        log_format = "%(asctime)-15s [%(loggername)-12s] %(levelname)s: %(logmsg)s"
        logging.basicConfig(format=log_format, filename=self.logfile, level=logging.DEBUG)

        while True:
            next_log_msg = self.logger_queue.get(True)

            d = dict({"loggername":str(next_log_msg.get('loggername')), \
                      "logmsg":str(next_log_msg.get('msg'))})

            if str(next_log_msg.get('type')) == "DEBUG":
                logging.debug("%s ", extra=d)
            elif str(next_log_msg.get('type')) == "INFO":
                logging.info("%s ", extra=d)
            elif str(next_log_msg.get('type')) == "WARNING":
                logging.warning("%s ", extra=d)
            elif str(next_log_msg.get('type')) == "ERROR":
                logging.error("%s ", extra=d)

            #if we don't know, we assume the worst
            else:
                logging.error("%s ", extra=d)
