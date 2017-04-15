########################################################################
# worker.py -- runs the actual tests of task results
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import datetime
from subprocess import Popen, PIPE

import common as c

class Worker(threading.Thread):
    """
    Thread that tests given user submissions.
    """

####
# __init__
####
    def __init__(self, name, job_queue, gen_queue, sender_queue, \
                 logger_queue, coursedb, semesterdb):
        """
        Constructor of the Worker thread.
        """

        threading.Thread.__init__(self)
        self.name = name
        self.job_queue = job_queue
        self.sender_queue = sender_queue
        self.logger_queue = logger_queue
        self.gen_queue = gen_queue
        self.coursedb = coursedb
        self.semesterdb = semesterdb

####
# get_task_parameters
####
    def get_task_parameters(self, uid, task_nr):
        """
        Look up the taskParmeters, that were generated from the generator for
        a indididual task.
        """

        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)
        data = {'task_nr': task_nr, 'uid': uid}
        sql_cmd = "SELECT TaskParameters FROM UserTasks WHERE TaskNr == :task_nr AND UserId == :uid"
        curs.execute(sql_cmd, data)
        params = curs.fetchone()[0]
        cons.close()
        return params

####
# run
####
    def run(self):
        """
        Thread code for the worker thread.
        """

        logmsg = "Starting " + self.name
        c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

        while True:
            logmsg = self.name + ": waiting for a new job."
            c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
            nextjob = self.job_queue.get(True)
            if nextjob:
                task_nr = nextjob.get('taskNr')
                user_id = nextjob.get('UserId')
                user_email = nextjob.get('UserEmail')
                message_id = nextjob.get('MessageId')

                logmsg = self.name + " got a new job: {0} from the user with id: {1}".format(str(task_nr), str(user_id))
                c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                # check if there is a test executable configured in the
                # database -- if not fall back on static test script.
                curc, conc = c.connect_to_db(self.coursedb, \
                                             self.logger_queue, self.name)
                try:
                    data = {'task_nr': task_nr}
                    sql_cmd = "SELECT TestExecutable FROM TaskConfiguration WHERE TaskNr == :task_nr"
                    curc.execute(sql_cmd, data)
                    testname = curc.fetchone()
                except:
                    logmsg = "Failed to fetch TestExecutable for TaskNr: {0}".format(task_nr)
                    logmsg = logmsg + " from the Database! Table TaskConfiguration corrupted?"
                    c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

                if testname != None:
                    try:
                        data = {'task_nr': task_nr}
                        sql_cmd = "SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == :task_nr"
                        curc.execute(sql_cmd, data)
                        path = curc.fetchone()
                        scriptpath = str(path[0]) + "/" + str(testname[0])
                    except: # if a testname was given, then a Path should be
                            # there as well!
                        logmsg = "Failed to fetch Path to Tasknr: {0}".format(task_nr)
                        logmsg = "{0} from the Database! Table TaskConfiguration corrupted?".format(logmsg)
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

                else: # in case no testname was given, we fall back to the
                      # static directory structure
                    scriptpath = "tasks/task" + str(task_nr) + "/./tests.sh"
                conc.close()

                # get the task parameters
                task_params = self.get_task_parameters(user_id, task_nr)

                # run the test script and log the stderr and stdout
                command = [scriptpath, str(user_id), str(task_nr), str(task_params)]
                logmsg = "Running test script with arguments: {0}".format(command)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                process = Popen(command, stdout=PIPE, stderr=PIPE)
                test_msg, test_error = process.communicate()
                test_msg = test_msg.decode('UTF-8')
                test_error = test_error.decode('UTF-8')
                test_res = process.returncode
                log_src = "Tester{0}({1})".format(str(task_nr), str(user_id))

                if test_msg:
                    c.log_task_msg(self.logger_queue, log_src, test_msg, "INFO")
                if test_error:
                    c.log_task_error(self.logger_queue, log_src, test_error, "ERROR")

                if test_res: # not 0 returned

                    logmsg = "Test failed! User: {0} Task: {1}".format(user_id, \
                                                                       task_nr)
                    logmsg = logmsg + " return value:" + str(test_res)
                    c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                    c.send_email(self.sender_queue, str(user_email), \
                                 str(user_id), "Failed", str(task_nr), "", \
                                 str(message_id))

                    if test_res == 2:
                        logmsg = "SecAlert: This test failed due to probable attack by user!"
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                        c.send_email(self.sender_queue, str(user_email), \
                                     str(user_id), "SecAlert", str(task_nr), "", \
                                     str(message_id))

                    elif test_res == 3:
                        logmsg = "TaskAlert: This test for TaskNr {0} and User {1} failed due an error with task/testbench analyzation!".format(task_nr, user_id)
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                        c.send_email(self.sender_queue, str(user_email), \
                                     str(user_id), "TaskAlert", str(task_nr), \
                                     "", str(message_id))

                else: # 0 returned
                    logmsg = "Test succeeded! User: {0} Task: {1}".format(user_id, task_nr)
                    c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                    # Notify, the user that the submission was successful
                    c.send_email(self.sender_queue, str(user_email), \
                                 str(user_id), "Success", str(task_nr), "", \
                                 str(message_id))

                    curc, conc = c.connect_to_db(self.coursedb, \
                                                 self.logger_queue, \
                                                 self.name)

                    currenttask = int(c.user_get_current_task(self.semesterdb, \
                                                             user_id, \
                                                             self.logger_queue, \
                                                             self.name))

                    # Next, a new Task is generated -- but only if a new task
                    # exists AND if a generator script exists  (otherwise
                    # static task description is assumed, AND if users current
                    # task < the task that shall be generated (no Task has yet
                    # been generated for this user yet).

                    if currenttask < int(task_nr)+1:
                        try:
                            data = {'task_nr': str(int(task_nr)+1)}
                            sql_cmd = "SELECT GeneratorExecutable FROM TaskConfiguration WHERE TaskNr == :task_nr"
                            curc.execute(sql_cmd, data)
                            res = curc.fetchone()
                        except:
                            logmsg = "Failed to fetch Generator Script for Tasknr: {0}".format(task_nr)
                            logmsg = logmsg + "from the Database! Table TaskConfiguration corrupted?"
                            c.log_a_msg(self.logger_queue, self.name, \
                                        logmsg, "ERROR")
                        finally:
                            conc.close()

                        task_start = c.get_task_starttime(self.coursedb, \
                                                          int(task_nr)+1, \
                                                          self.logger_queue, \
                                                          self.name)

                        if task_start < datetime.datetime.now():
                            if res != None: # generator script for this task configured?
                                logmsg = "Calling Generator Script: " + str(res[0])
                                c.log_a_msg(self.logger_queue, self.name, \
                                            logmsg, "DEBUG")
                                logmsg = "UserID {0}, UserEmail {1}".format(user_id, user_email)
                                c.log_a_msg(self.logger_queue, self.name, \
                                            logmsg, "DEBUG")

                                self.gen_queue.put(dict({"user_id": str(user_id), \
                                         "user_email": str(user_email), \
                                         "task_nr": str(int(task_nr)+1), \
                                         "messageid": ""}))
                            else:
                                c.send_email(self.sender_queue, \
                                             str(user_email), str(user_id), \
                                             "Task", str(int(task_nr)+1), "", \
                                             str(message_id))

                        else:
                            c.send_email(self.sender_queue, str(user_email), \
                                         str(user_id), "CurLast", \
                                         str(int(task_nr)+1), "", \
                                         str(message_id))
