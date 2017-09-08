##########################################################################
# activator.py -- check periodically, if the starttime of a task has come.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
##########################################################################

import threading
import time
import datetime

import common as c

class TaskActivator(threading.Thread):
    """
    Thread in charge of checking periodically every 30 minutes if a task should
    activated (TaskStart < now) and initiate the task generations for users
    waiting for this task
    """

    def __init__(self, name, queues, dbs, auto_advance):
        """
        Constructor for the activator thread
        """

        threading.Thread.__init__(self)
        self.name = name
        self.queues = queues
        self.dbs = dbs
        self.auto_advance = auto_advance

    def activator_loop(self):
        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"],\
                                     self.name)

        # first we need to know, which tasks are not active at the moment
        sql_cmd = "SELECT * FROM TaskConfiguration WHERE TaskActive = 0"
        curc.execute(sql_cmd)
        rows_tasks = curc.fetchall()

        # loop through all the inactive tasks
        for row_task in rows_tasks:
            task_nr = row_task[0]
            logmsg = "Task {0} is still inactive".format(str(task_nr))
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

            # check if a tasks start time has come
            task_start = datetime.datetime.strptime(row_task[1], c.format_string)
            if task_start < datetime.datetime.now():
                # first, let's set the task active!
                data = {'task_nr': task_nr}
                sql_cmd = ("UPDATE TaskConfiguration SET TaskActive = 1 "
                           "WHERE TaskNr = :task_nr")
                curc.execute(sql_cmd, data)
                conc.commit()
                logmsg = "Turned Task {0} to active.".format(str(task_nr))
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

                curs, cons = c.connect_to_db(self.dbs["semester"], \
                                             self.queues["logger"], self.name)

                # if auto_advance is activated, all users should be
                # advanced to that task
                if self.auto_advance:
                    data = {'task_nr': task_nr}
                    sqlcmd = ("SELECT UserId FROM Users "
                              "WHERE CurrentTask < :task_nr")
                    curs.execute(sqlcmd, data)
                    rows = curs.fetchall()

                    users_list = []
                    for row in rows:
                        users_list.append(str(row[0]))
                    users_comma_list = ','.join(users_list)

                   # This did not work, therefore with format:
                   # data = {'task_nr': task_nr,\
                   #         'users_comma_list': users_comma_list}
                   # sqlcmd = ("UPDATE Users SET CurrentTask = :task_nr "
                   #           " WHERE UserId IN (:users_comma_list)")
                   # curs.execute(sqlcmd, data)

                    sqlcmd = ("UPDATE Users SET CurrentTask = {0} WHERE "
                              "UserId in ({1});").format(task_nr, users_comma_list)
                    curs.execute(sqlcmd)
                    cons.commit()
                    logmsg = "Advanced users with ids: " + users_comma_list
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

                # next, check if any users are waiting for that task, meaning:
                # 1) his CurrentTask = task_nr AND 2) No UserTask exists for it
                #TODO: Find a better solution with a join
                data = {'task_nr': task_nr}
                sqlcmd = ("SELECT UserId, Email FROM Users "
                          "WHERE CurrentTask = :task_nr AND UserId NOT IN "
                          "(SELECT UserId FROM UserTasks "
                          "WHERE TaskNr = :task_nr)")
                curs.execute(sqlcmd, data)

                rows = curs.fetchall()
                for row in rows:
                    user_id = row[0]
                    user_email = row[1]

                    logmsg = "The next task({0}) is sent to User {1} now." \
                        .format(task_nr, user_id)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

                    try:
                        data = {'task_nr': task_nr}
                        sql_cmd = ("SELECT GeneratorExecutable FROM TaskConfiguration "
                                   "WHERE TaskNr = :task_nr")
                        curc.execute(sql_cmd, data)
                        res = curc.fetchone()
                    except:
                        logmsg = ("Failed to fetch Generator Script for"
                                  "TaskNr {0} from the Database! Table "
                                  "TaskConfiguration corrupted?").format(task_nr)
                        c.log_a_msg(self.queues["logger"], self.name, \
                                    logmsg, "ERROR")

                    if res != None:
                        logmsg = "Calling Generator Script: {0}".format(res[0])
                        c.log_a_msg(self.queues["logger"], self.name, \
                                    logmsg, "DEBUG")

                        logmsg = "UserEmail: {0}, TaskNr : {1}, UserId: {2},"\
                                 .format(user_email, task_nr, user_id)
                        c.log_a_msg(self.queues["logger"], self.name, \
                                    logmsg, "DEBUG")

                        c.generate_task(self.queues["generator"], user_id,\
                                        task_nr, user_email, "")

                    else:
                        c.send_email(self.queues["sender"], str(user_email), \
                                     str(user_id), "Task", str(task_nr), "", "")
                cons.close()
        conc.close()

####
# thread code for the worker thread.
####
    def run(self):
        logmsg = "Starting " + self.name
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        while True:
            self.activator_loop()
            time.sleep(1800) # it's more than enough to check every half hour
