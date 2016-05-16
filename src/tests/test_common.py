import queue
import common
import logger
import unittest
import time
import os

class test_common(unittest.TestCase):
    def setUp(self):
        self.logger_queue = queue.Queue(10)
        self.lfile = "/tmp/test_logfile"
        # Before we do anything else: start the logger thread
        # so we can log whats going on
        thread_id = 1
        logger_t = logger.autosubLogger(thread_id, "logger", self.logger_queue, self.lfile)
        logger_t.daemon = True # make the logger thread a daemon, this way the main
                        # will clean it up before terminating!
        logger_t.start()

    def check_last_log_entry(self, logmsg, loglvl):
        common.log_a_msg(self.logger_queue, "testlogger", logmsg, loglvl)
        time.sleep(.25) # give the logger some time...

        with open(self.lfile, "r") as fd_log:
            for line in fd_log.readlines():
                #nothing - only interested in the very last line!
                pass

            self.assertNotEqual(line.find(logmsg), str(-1))
            self.assertNotEqual(line.find(loglvl), str(-1))

    def test_log_a_msg(self):
        print("Testing Function: log_a_msg()")

        self.check_last_log_entry("Test Message Nr. 1", "DEBUG")
        self.check_last_log_entry("Test Message Nr. 2", "INFO")
        self.check_last_log_entry("ABABABABABABABABABBABABABABABABAB", "WARNING")
        self.check_last_log_entry("", "ERROR")
        self.check_last_log_entry("TestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTestTest", "INFO")

    def test_check_dir_mkdir(self):
        print("Testing Function: check_dir_mkdir()")

        self.assertEqual(common.check_dir_mkdir('testdir', self.logger_queue, "testlogger"), 1)
        self.assertEqual(common.check_dir_mkdir('testdir', self.logger_queue, "testlogger"), 0)

        os.rmdir('testdir')

if __name__ == '__main__':
    unittest.main()
