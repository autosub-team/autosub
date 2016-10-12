##########################################################################
# activator.py -- check periodically, if the starttime of a task has come.
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
##########################################################################

import threading
import common as c
import time
import datetime

class TaskActivator(threading.Thread):
    def __init__(self, name, gen_queue, sender_queue, logger_queue, \
                 coursedb, semesterdb, auto_advance):
        threading.Thread.__init__(self)
        self.name = name
        self.sender_queue = sender_queue
        self.logger_queue = logger_queue
        self.gen_queue = gen_queue
        self.coursedb = coursedb
        self.semesterdb = semesterdb
        self.auto_advance = auto_advance

    def activator_loop(self):
        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, \
                                     self.name)

        # first we need to know, which tasks are not active at the moment
        sql_cmd = "SELECT * FROM TaskConfiguration WHERE TaskActive==0;"
        curc.execute(sql_cmd)
        rows_tasks = curc.fetchall

        # loop through all the inactive tasks
        for row_task in rows_task:
            tasknr = row_task[0]
            logmsg = "Task {0} is still inactive".format(str(tasknr))
            c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

            # check if a tasks start time has come
            task_starttime = datetime.datetime.strptime(row_task[1], c.format_string)
            if task_starttime < datetime.datetime.now():
                # first, let's set the task active!
                data = {'tasknr': tasknr}
                sql_cmd = "UPDATE TaskConfiguration SET TaskActive = 1 WHERE TaskNr == :tasknr;"
                curc.execute(sql_cmd, data)
                conc.commit()
                logmsg = "Turned Task {0} to active.".format(str(tasknr))
                c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                # if auto_advance is activated, all users should be
                # advanced to that task
                if self.auto_advance = True:
                    data = {'tasknr': tasknr}
                    sqlcmd = "SELECT UserId FROM Users WHERE CurrentTas < :tasknr;"
                    curs.execute(sqlcmd, data)
                    rows = curs.fetchall()

                    users_list = []
                    for row in rows:
                        users_list.append(row[0])
                    users_comma_list = ','.join (users_list)

                    data = {'tasknr': tasknr, 'users_list': users_lis)
                    sqlcmd = ("UPDATE Users SET CurrenTask = :tasknr WHERE "
                                  "UserId IN (:users_comma_list);")
                    curs.execute(sqlcmd, data)
                    curs.commit()

                # next, check if any users are waiting for that task
                curs, cons = c.connect_to_db(self.semesterdb, \
                                             self.logger_queue, self.name)
                data = {'tasknr': tasknr}
                sqlcmd = "SELECT * FROM Users WHERE CurrentTask == :tasknr;"
                curs.execute(sqlcmd, data)

                rows = curs.fetall()
                for row in rows:
                    uid = row[0]
                    user_email = row[2]

                    logmsg = "The next task({0} is sent to User {1} now." \
                        .format(tasknr, uid)
                    c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
                    
                    try:
                        data = {'tasknr': tasknr}
                        sql_cmd = "SELECT GeneratorExecutable FROM TaskConfiguration WHERE TaskNr == :tasknr;"
                        curc.execute(sql_cmd, data)
                        res = curc.fetchone()
                    except:
                        logmsg = "Failed to fetch Generator Script for Tasknr: "+ str(tasknr)
                        logmsg = logmsg + "from the Database! Table TaskConfiguration corrupted?"
                        c.log_a_msg(self.logger_queue, self.name, \
                                    logmsg, "ERROR")

                    if res != None:
                        logmsg = "Calling Generator Script: {0}".format(res[0])
                        c.log_a_msg(self.logger_queue, self.name, \
                                    logmsg, "DEBUG")

                        logmsg = "UserEmail: {0}, TaskNr : {1}, UserId: {0},".format(user_email, \
                                                                                     tasknr, uid)
                        c.log_a_msg(self.logger_queue, self.name, \
                                    logmsg, "DEBUG")
                        self.gen_queue.put(dict({"user_id": str(uid), \
                                                 "user_email": str(user_email), \
                                                 "task_nr": str(tasknr), \
                                                 "messageid": ""}))
                    else:
                        c.send_email(self.sender_queue, str(user_email), \
                                     str(uid), "Task", str(tasknr), "", "")
                cons.close()
        conc.close()

####
# thread code for the worker thread.
####
    def run(self):
        logmsg = "Starting " + self.name
        c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

        while True:
            self.activator_loop()
            time.sleep(3600) # it's more than enough to check every hour!


