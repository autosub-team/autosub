########################################################################
# fetcher.py -- fetch e-mails from the mailbox
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

########################################################################
# Implementation Note:
#    The fetcher needs to be able to store data to uniquely identify
#    emails to remember backlogged messages and move processed messages.
#    IMAP offers different values to do so: 1) message number: the
#    position of the mail in the mailbox, this changs when a mail is
#    moved; 2) UID: unique id per mailbox, can change between sessions,
#    changes are shown by change of uidvalidity status; 3) Message Id:
#    number given by the sending SMTP server; A email can only be
#    selectively fetched via uid or message number. It was chosen to
#    store and pass Message Ids. This has the disadvantage, that for an
#    action all the emails in the inbox have to be fetched and then each
#    compared to the stored Message Id. This should not be a big
#    problem for performance, as processed emails are moved to the
#    archive folder (which should exist!!!!)
########################################################################

import threading
import email
import imaplib
import os
import time
import re #regex
import datetime
import queue

import common as c

class MailFetcher(threading.Thread):
    """
    Thread in charge of fetching emails from IMAP and based on these emails
    assigns work to other threads.
    """

    def __init__(self, name, queues, dbs, imap_info, poll_period, \
                 allow_skipping):
        """
        Constructor for fetcher thread
        """

        threading.Thread.__init__(self)
        self.name = name
        self.queues = queues
        self.dbs = dbs
        self.imap_info = imap_info
        self.poll_period = poll_period
        self.allow_skipping = allow_skipping

        # for backlog handling
        self.mid_to_job_tuple = {}
        self.jobs_backlog = {}
        self.jobs_active = {}

    ####
    # get_admin_emails
    ####
    def get_admin_emails(self):
        """
        Get the email adresses of all configured admins.

        Return a list.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        sql_cmd = ("SELECT Content FROM GeneralConfig "
                  "WHERE ConfigItem == 'admin_email'")
        curc.execute(sql_cmd)
        result = curc.fetchone()
        if result != None:
            result = str(result[0])
            admin_emails = [email.strip() for email in result.split(',')]
        else:
            admin_emails = []

        conc.close()

        return admin_emails

    ####
    # get_taskoperator_emails
    ####
    def get_taskoperator_emails(self, task_nr):
        """
        Get the email adresses of all configured operators for a specific task.

        Return a list.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'TaskNr': task_nr}
        sql_cmd = ("SELECT TaskOperator FROM TaskConfiguration "
                   "WHERE TaskNr = :TaskNr")
        curc.execute(sql_cmd, data)
        result = curc.fetchone()
        if result != None:
            result = str(result[0])
            taskoperator_emails = [email.strip() for email in result.split(',')]
        else:
            taskoperator_emails = []

        conc.close()

        return taskoperator_emails


    ####
    # add_new_user
    ####
    def add_new_user(self, user_name, user_email):
        """
        Add the necessary entries to database for a newly registered user.
        Call generator thread to create the first task.
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)

        logmsg = 'Creating new Account: User: %s' % user_name
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        data = {'Name': user_name, 'Email': user_email, 'TimeNow': str(int(time.time()))}
        sql_cmd = ("INSERT INTO Users "
                   "(UserId, Name, Email, FirstMail, LastDone, CurrentTask) "
                   "VALUES(NULL, :Name, :Email, datetime(:TimeNow, 'unixepoch', 'localtime')"
                   ", NULL, 1)")
        curs.execute(sql_cmd, data)
        cons.commit()

        # the new user has now been added to the database. Next we need
        # to send him an email with the first task.

        # read back the new users UserId and create a directory for putting his
        # submissions in.
        data = {'Email': user_email}
        sql_cmd = "SELECT UserId FROM Users WHERE Email = :Email"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        if res is None:
            logmsg = ("Created new user with "
                      "name= {0} , email={1} failed").format(user_name, user_email)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        user_id = str(res[0])
        dir_name = 'users/'+ user_id
        c.check_dir_mkdir(dir_name, self.queues["logger"], self.name)

        cons.close()

        # Give the user the task which is starttime <= now < deadline AND
        # min(TaskNr)
        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'TimeNow': str(int(time.time()))}
        sql_cmd = ("SELECT MIN(TaskNr) FROM TaskConfiguration "
                   "WHERE TaskStart <= datetime(:TimeNow, 'unixepoch','localtime') AND "
                   "TaskDeadline > datetime(:TimeNow, 'unixepoch', 'localtime')")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        conc.close()

        if not res or not res[0]:
            logmsg = ("Error generating first Task for UserId = {0}. Could not "
                      "find first task for this user").format(user_id)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
        else:
            task_nr = int(res[0])

            #adjust users CurrentTask if he does not get Task with task_nr=1
            if task_nr != 1:
                c.user_set_current_task(self.dbs["semester"], task_nr, user_id, \
                                        self.queues["logger"], self.name)

            logmsg = ("Calling Generator to create"
                      "TaskNr:{0} for UserId:{1}").format(task_nr, user_id)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            c.generate_task(self.queues["generator"], user_id, task_nr, user_email, "")

    ###
    # increment_submission_nr
    ##
    def increment_submission_nr(self, user_id, task_nr):
        """
        Increment submission number for a specific user and task.

        Return new number or 0 if no previous submission for this task exists.
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)

        try:
            data = {'UserId':user_id, 'TaskNr': task_nr}
            sql_cmd = ("UPDATE UserTasks SET NrSubmissions = NrSubmissions+1 "
                       "WHERE UserId = :UserId AND TaskNr = :TaskNr")
            curs.execute(sql_cmd, data)
            cons.commit()

            sql_cmd = ("SELECT NrSubmissions from UserTasks "
                       "WHERE UserId = :UserId AND TaskNr = :TaskNr")
            curs.execute(sql_cmd, data)
            res = curs.fetchone()

            cons.close()

            return int(res[0])
        except:
            cons.close()

            return 0

    ####
    # save_submission_user_dir
    ####
    def save_submission_user_dir(self, user_id, task_nr, mail):
        """
        Store a new submisson in the user's directory structure.
        """

        # increment the submission_nr for the user
        submission_nr = self.increment_submission_nr(int(user_id), int(task_nr))

        #create a directory for putting his submission in:
        detach_dir = 'users/{0}/Task{1}'.format(user_id, task_nr)
        ts = datetime.datetime.now()
        submission_dir = "/Submission{0}_{1}{2}{3}_{4}{5}{6}{7}".format(\
            submission_nr, ts.year, ts.month, ts.day, ts.hour, ts.minute, \
            ts.second, ts.microsecond)
        current_dir = detach_dir + submission_dir
        c.check_dir_mkdir(current_dir, self.queues["logger"], self.name)

        # use walk to create a generator, iterate on the parts and forget
        # about the recursive headache
        for part in mail.walk():
        # multipart are just containers, so skip them
            if part.get_content_maintype() == 'multipart':
                continue

            # is this part an attachment ?
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            counter = 1

            # no filename? -> create one with a counter to avoid duplicates
            if not filename:
                filename = 'part-%03d%s' % (counter, 'bin')
                counter += 1

            att_path = os.path.join(current_dir, filename)

            #Check if its already there
            if not os.path.isfile(att_path):
                # finally write the stuff
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

        cmd = "rm " + detach_dir + "/*" + " 2> /dev/null"
        os.system(cmd)

        cmd = "cp -R " +  current_dir + "/* " + detach_dir + " 2> /dev/null"
        os.system(cmd)

    ####
    # get_archive_dir
    ###
    def get_archive_dir(self):
        """
        Get the  name of the directory processed mails shall be moved to
        on the IMAP server
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)

        data = {'config_item':'archive_dir'}
        sql_cmd = ("SELECT Content FROM GeneralConfig "
                   "WHERE ConfigItem= :config_item")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()

        archive_dir = str(res[0])

        conc.close()

        return archive_dir

    ####
    # a_question_was_asked
    ###
    def a_question_was_asked(self, user_id, user_email, mail, message_id):
        """
        Process a question that was asked by a user.
        """

        mail_subject = str(mail['subject'])

        logmsg = 'The user has a question, please take care of that!'
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
        c.send_email(self.queues["sender"], user_email, "", "Question", "", "", "")

        # was the question asked to a specific task_nr that is valid?
        search_obj = re.search('[0-9]+', mail_subject, )

        if (search_obj != None) and int(search_obj.group()) <= c.get_num_tasks(self.dbs["course"], \
                                            self.queues["logger"], self.name):
            tasknr = search_obj.group()
            fwd_mails = self.get_taskoperator_emails(tasknr)
            if not fwd_mails:
                logmsg = ("Error getting the taskoperator email for task {0}. "
                          "Question from user with email={1} "
                          "dropped.").format(tasknr, user_email)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                return
        else:
            fwd_mails = self.get_admin_emails()
            if not fwd_mails:
                logmsg = ("Error getting the admin email for task {0}. "
                          "Question from user with email={1} "
                          "dropped.").format(tasknr, user_email)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                return

        for mail_address in fwd_mails:
            c.send_email(self.queues["sender"], mail_address, user_id, "QFwd", "", mail, message_id)

        c.increment_db_statcounter(self.dbs["semester"], 'nr_questions_received', \
                                   self.queues["logger"], self.name)


    ####
    # a_status_is_requested
    ####
    def a_status_is_requested(self, user_id, user_email, message_id):
        """
        Tell sender to send out a status email.
        """

        logmsg = ("STATUS requested: User with UserId:{0}, Email: {1}").format(\
                 user_id, user_email)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)

        data = {'user_id':user_id}
        sql_cmd = "SELECT CurrentTask FROM Users WHERE UserId == :user_id"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        current_task = res[0]

        cons.close()

        c.send_email(self.queues["sender"], user_email, user_id, "Status", current_task, \
                     "", message_id)
        c.increment_db_statcounter(self.dbs["semester"], 'nr_status_requests', \
                                   self.queues["logger"], self.name)

    ####
    # a_result_was_submitted
    ####
    def a_result_was_submitted(self, user_id, user_email, task_nr, message_id, \
                               mail):
        """
        Check if the user is allowed ot submit a result to the task
        with given task nr and if yes add to worker queue.
        """

        logmsg = "Processing a Result, UserId:{0} TaskNr:{1}"\
                .format(user_id, task_nr)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        # at which task_nr is the user
        cur_task = c.user_get_current_task(self.dbs["semester"], user_id, self.queues["logger"], \
                                      self.name)

        #task with this tasknr exists?
        is_task = c.is_valid_task_nr(self.dbs["course"], task_nr, self.queues["logger"],\
                                     self.name)

        if not is_task:
        # task_nr is not valid
            c.send_email(self.queues["sender"], user_email, "", "InvalidTask", str(task_nr), \
                         "", message_id)
            return

        # task_nr is valid, get deadline
        deadline = c.get_task_deadline(self.dbs["course"], task_nr, self.queues["logger"], \
                                           self.name)

        if is_task and cur_task < int(task_nr):
        #task_nr valid, but user has not reached that tasknr yet
            logmsg = ("User can not submit for this task yet.")
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            c.send_email(self.queues["sender"], user_email, "", "TaskNotSubmittable", str(task_nr), \
                         "", message_id)

        elif deadline < datetime.datetime.now():
        # deadline passed for that task_nr!
            logmsg = ("Deadline passed")
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            c.send_email(self.queues["sender"], user_email, "", "DeadTask", str(task_nr), \
                         "", message_id)

        else:
        # okay, let's work with the submission

            job_tuple = (user_id, task_nr)
            dispatchable = job_tuple not in self.jobs_active

            if not dispatchable:
                if job_tuple in self.jobs_backlog:
                    self.jobs_backlog[job_tuple].append(message_id)
                else:
                    self.jobs_backlog[job_tuple] = [message_id]

                logmsg = ("Backlogged {0},{1},{2}").format(user_id, task_nr, message_id)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")


            else:
                # save the attached files to user task directory
                self.save_submission_user_dir(user_id, task_nr, mail)

                c.dispatch_job(self.queues["job"], user_id, task_nr, \
                                   user_email, message_id)

                dispatch_time = time.time()

                self.jobs_active[job_tuple] = {"dispatch": dispatch_time, \
                                               "message_id": message_id}
                self.mid_to_job_tuple[message_id] = job_tuple

    ####
    # skip_was_requested
    ####
    def skip_was_requested(self, user_id, user_email, message_id):
        """
        Process a requested skip, check if skip is possible, if yes
        put job in generator queue.
        """

        # at which task_nr is the user?
        cur_task = c.user_get_current_task(self.dbs["semester"], user_id, self.queues["logger"], \
                                           self.name)
        next_task = cur_task + 1

        logmsg = ("Skip requested: User with UserId:{0}, from "
                  "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        #task with this tasknr exists?
        is_task = c.is_valid_task_nr(self.dbs["course"], next_task, self.queues["logger"],\
                                     self.name)
        if is_task:
            task_starttime = c.get_task_starttime(self.dbs["course"], next_task,
                                                  self.queues["logger"], self.name)
            task_has_started = task_starttime < datetime.datetime.now()

            if task_has_started:
                #set new current task
                c.user_set_current_task(self.dbs["semester"], next_task, user_id, \
                                        self.queues["logger"], self.name)

                #tell generator thread to create new task
                logmsg = ("Calling Generator to create "
                          "TaskNr:{0} for UserId:{1}").format(next_task, user_id)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

                c.generate_task(self.queues["generator"], user_id, next_task, user_email, message_id)

                logmsg = ("Skip done: User with UserId:{0}, from "
                          "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

                return

        #Skip not possible
        logmsg = ("Skip NOT POSSIBLE: User with UserId:{0}, from "
                  "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        c.send_email(self.queues["sender"], user_email, "", "SkipNotPossible", \
                     "", "", message_id)

    ####
    # connect_to_imapserver
    ####
    def connect_to_imapserver(self):
        """
        Connect to configured IMAP server.
        """

        try:
            # connecting to the imap server
            if self.imap_info["security"] == 'ssl':
                server = imaplib.IMAP4_SSL(self.imap_info["server"], int(self.imap_info["port"]))
            else:
                server = imaplib.IMAP4(self.imap_info["server"], int(self.imap_info["port"]))

            if self.imap_info["security"] == 'starttls':
                server.starttls()

            server.login(self.imap_info["user"], self.imap_info["passwd"])
        except imaplib.IMAP4.abort:
            logmsg = "Login to server was aborted with security= " + self.imap_info["security"] + \
                     " , port= " + str(self.imap_info["port"])
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            #m.close()
            return 0
        except imaplib.IMAP4.error:
            logmsg = "Got an error when trying to connect to the imap server with" + \
                     " security= " + self.imap_info["security"] + " , port= " + str(self.imap_info["port"])
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return 0
        except Exception as e:
            logmsg = str(e)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            logmsg = "Got an unknown exception when trying to connect to the imap " + \
                     "server with security= " + self.imap_info["security"] + " , port= " + str(self.imap_info["port"])
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return 0

        logmsg = "Successfully logged into imap server with security= " + self.imap_info["security"] + \
                 " , port= " + str(self.imap_info["port"])
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

        return server

    ####
    # disconnect_from_imapserver
    ####
    def disconnect_from_imapserver(self, m):
        """
        Disconnect from existing imap connection
        """

        # m==0 is only possible in test-code (e.g. load_test.py)
        if m != 0:
            try:
                m.close()
                m.logout()
                logmsg = "closed connection to imapserver"
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")
            except:
                logmsg = "Got an error when trying to disconnect from the imap server."
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

    ####
    # idmap_new_emails(self, m):
    ####
    def idmap_new_emails(self, m):
        """
        Search for new (unseen) e-mails from the Inbox.

        Return a mapping as dict that assigns each Message-Id its UID.
        """

        try:
            m.select("Inbox") # here you a can choose a mail box like INBOX instead
            # use m.list() to get all the mailboxes
        except:
            logmsg = "Failed to select inbox"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return {}

        idmap = dict()

        # you could filter using the IMAP rules here
        # (check http://www.example-code.com/csharp/imap-search-critera.asp)

        #resp, data = m.search(None, "UNSEEN")
        resp, data = m.uid('search', None, "UNSEEN")

        if resp == 'OK':
            for uid in data[0].split():
                typ, msg_data = m.uid('fetch', uid, "(BODY[HEADER])")
                mail = email.message_from_bytes(msg_data[0][1])
                idmap[mail['Message-ID']] = uid

            return idmap

        else:
            logmsg = "Failed to get messages from inbox"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return {}


    ####
    # idmap_all_emails(self, m):
    ####
    def idmap_all_emails(self, m):
        """
        Search for all emails.

        Return a mapping as dict that assigns each Message-Id its UID.
        """

        try:
            m.select(mailbox='Inbox', readonly=False)
        except:
            logmsg = "Failed to select inbox"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return {}

        idmap = dict()

        # you could filter using the IMAP rules here
        # (check http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = m.uid('search', None, "ALL")


        if resp == 'OK':
            for uid in items[0].split():
                typ, msg_data = m.uid('fetch', uid, "(BODY[HEADER])")
                mail = email.message_from_bytes(msg_data[0][1])
                idmap[mail['Message-ID']] = uid

            return idmap
        else:
            logmsg = "Failed to get messages from inbox"
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return {}

    ####
    # check_if_whitelisted
    ####
    def check_if_whitelisted(self, user_email):
        """
        Check if the given e-mail address is in the whitelist.
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)

        data = {'Email': user_email}
        sql_cmd = "SELECT * FROM WhiteList WHERE Email == :Email"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()

        cons.close()

        if res != None:
            return True

        else:
            logmsg = "Got Mail from a User not on the WhiteList: " + user_email
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "Warning")
            c.increment_db_statcounter(self.dbs["semester"], 'nr_non_registered', \
                                       self.queues["logger"], self.name)

            return False

    ####
    # get_registration_deadline
    ####
    def get_registration_deadline(self):
        """
        Get the registration deadline datetime.

        Return datetime, if not found return 1 hour from now.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], self.name)
        sql_cmd = ("SELECT Content FROM GeneralConfig " \
                   "WHERE ConfigItem == 'registration_deadline'")
        curc.execute(sql_cmd)
        deadline_string = str(curc.fetchone()[0])

        conc.close()

        format_string = '%Y-%m-%d %H:%M:%S'
        if deadline_string != 'NULL':
            return datetime.datetime.strptime(deadline_string, format_string)

        else:
             # there is no deadline set, just assume it is in 1h from now.
            date = datetime.datetime.now() + datetime.timedelta(0, 3600)

            logmsg = "No Registration Deadline found, assuming: " + str(date)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

            return date

    ####
    # action_by_subject
    ####
    def action_by_subject(self, user_id, user_email, message_id, mail, mail_subject):
        """
        Examine the subject of the users email and initiate appropiate action
        """

        if re.search('[Rr][Ee][Ss][Uu][Ll][Tt]', mail_subject):
        ###############
        #   RESULT    #
        ###############
            search_obj = re.search('[0-9]+', mail_subject)
            if search_obj is None:
            # Result + no number
                logmsg = ("Got a kind of message I do not understand. "
                          "Sending a usage mail...")
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")
                c.send_email(self.queues["sender"], user_email, "", "Usage", "", \
                             "", message_id)
                return

            #Result + number
            task_nr = search_obj.group()

            self.a_result_was_submitted(user_id, user_email, task_nr, message_id, \
                                        mail)

        elif re.search('[Qq][Uu][Ee][Ss][Tt][Ii][Oo][Nn]', mail_subject):
        ###############
        #   QUESTION  #
        ###############
            self.a_question_was_asked(user_id, user_email, mail, message_id)

        elif re.search('[Ss][Tt][Aa][Tt][Uu][Ss]', mail_subject):
        ###############
        #   STATUS    #
        ###############
            self.a_status_is_requested(user_id, user_email, message_id)

        elif self.allow_skipping and re.search('[Ss][Kk][Ii][Pp]', mail_subject):
        ####################
        # SKIP, IF ALLOWED #
        ####################
            self.skip_was_requested(user_id, user_email, message_id)

        else:
        #####################
        #   DEFAULT ACTION  #
        #####################
            logmsg = ("Got a kind of message I do not understand. "
                      "Sending a usage mail...")
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")
            c.send_email(self.queues["sender"], user_email, "", "Usage", "", \
                         "", message_id)

    ####
    # handle_backlogged
    ####
    def handle_backlogged(self, m):
        """
        Handle backlogged result emails. Only one (user_id, task_nr) job
        tuple can be dispatched at the same time.
        """

        if len(self.jobs_backlog) == 0:
            return

        uid_of_mid = self.idmap_all_emails(m)

        # if there is a active_job, that should be force removed when
        # (dispatch - now) > 5min
        time_now = time.time()
        to_delete = []

        for job_tuple, job_info in self.jobs_active.items():
            dispatch = job_info["dispatch"]
            if (dispatch - time_now) > 300:
                to_delete.append(job_tuple)

        for job_tuple in to_delete:
            del self.jobs_active[job_tuple]
            #TODO: log this?

        # can a backlogged job be dispatched?
        dispatch_time = time.time()
        to_delete = []

        for job_tuple, message_ids in self.jobs_backlog.items():

            # job_tuple job not already active
            if not job_tuple in self.jobs_active:
                # first backlogged message_id
                message_id = message_ids[0]

                try:
                    # get the message from server
                    uid = uid_of_mid[message_id]
                    resp, data = m.uid('fetch', uid, "(RFC822)")
                    mail = email.message_from_bytes(data[0][1])

                    user_id = job_tuple[0]
                    task_nr = job_tuple[1]

                    from_header = str(mail['From'])
                    split_header = str(from_header).split("<")

                    try:
                        user_email = str(split_header[1].split(">")[0])
                    except:
                        user_email = str(mail['From'])
                    # save the attached files to user task directory
                    self.save_submission_user_dir(user_id, task_nr, mail)

                    c.dispatch_job(self.queues["job"], user_id, task_nr, \
                                   user_email, message_id)

                    self.jobs_active[job_tuple] = {"dispatch": dispatch_time, \
                                                   "message_id": message_id}
                    self.mid_to_job_tuple[message_id] = job_tuple

                    logmsg = ("Dispatched backlogged {0},{1},{2}").format(user_id, task_nr, message_id)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "INF")

                except:
                    logmsg = ("Error while dispatching backlogged task UserId = {0} "
                              "TaskNr = {1} MessageId = {2}").format(user_id, task_nr, \
                                                                     message_id)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

                # delete the message_id from backlog, if no more backlog for this
                # job_tuple then mark for deletion of whole entry
                del message_ids[0]
                if len(self.jobs_backlog[job_tuple]) == 0:
                    to_delete.append(job_tuple)

        for job_tuple in to_delete:
            del self.jobs_backlog[job_tuple]

    ####
    # archive_processed
    ####
    def archive_processed(self, m):
        """
        Archive mails which are in the archive queue and therefore have been
        fully processed (copy & delete = move).
        """

        archive_dir = self.get_archive_dir()
        uid_of_mid = self.idmap_all_emails(m)

        # process queue, as soon as no next item available immediately return
        while True:
            try:
                next_archive_msg = self.queues["archive"].get_nowait()
            except queue.Empty:
                return

            message_id = next_archive_msg.get('mid')
            is_finished_job = next_archive_msg.get('isfinishedjob')

            # find uid for the mid
            logmsg = "Moving Message with ID: {0}".format(message_id)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
            try:
                uid = uid_of_mid[message_id]
            except KeyError:
                logmsg = ("Error moving message: could not find uid for Message"
                          "with ID: {0}").format(message_id)
                continue

            if is_finished_job:
                job_tuple = self.mid_to_job_tuple[message_id]
                del self.jobs_active[job_tuple]
                del self.mid_to_job_tuple[message_id]

            # copy
            result = m.uid('COPY', uid, archive_dir)

            # delete
            if result[0] == 'OK':
                m.uid('STORE', uid, '+FLAGS', '(\Deleted)')
                m.expunge()
            else:
                log_msg = ("Error moving a message. Is the "
                           "configured archive_dir '{0}' existing "
                           "on the IMAP server?!").format(archive_dir)
                c.log_a_msg(self.queues["logger"], self.name, \
                            log_msg, "ERROR")

    ####
    # handle_new
    ####
    def handle_new(self, m):
        """
        Fetch new emails and initiate appropriate action
        """

        uid_of_mid = self.idmap_new_emails(m)

        if uid_of_mid is None:
            return

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], self.name)

        # iterate over all new e-mails and take action according to the structure
        # of the subject line
        for message_id, uid in uid_of_mid.items():
            c.increment_db_statcounter(self.dbs["semester"], 'nr_mails_fetched', \
                                       self.queues["logger"], self.name)

            # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you
            # can ask for headers only, etc
            resp, data = m.uid('fetch', uid, "(RFC822)")

            # parsing the mail content to get a mail object
            mail = email.message_from_bytes(data[0][1])

            mail_subject = str(mail['subject'])
            from_header = str(mail['From'])
            split_header = str(from_header).split("<")
            user_name = split_header[0]

            try:
                user_email = str(split_header[1].split(">")[0])
            except:
                user_email = str(mail['From'])

            # Now let's decide what actions to take with the received email
            whitelisted = self.check_if_whitelisted(user_email)
            if whitelisted:
            # On Whitelist
                data = {'Email': user_email}
                sql_cmd = "SELECT UserId FROM Users WHERE Email = :Email"
                curs.execute(sql_cmd, data)
                res = curs.fetchone()

                if res != None:
                # Already registered
                    user_id = res[0]
                    logmsg = ("Got mail from an already known user! "
                              "(UserId:{0}, Email:{1}").format(user_id, user_email)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "INFO")

                    # Take action based on the subject
                    self.action_by_subject(user_id, user_email, message_id, mail, \
                                      mail_subject)

                else:
                # Not yet registered
                    reg_deadline = self.get_registration_deadline()

                    if reg_deadline > datetime.datetime.now():
                    # Before Registraton deadline?
                        #Name for user specified in Whitelist? -> take it
                        data = {'Email': user_email}
                        sql_cmd = ("SELECT Name FROM Whitelist "
                                   "WHERE Email = :Email")
                        curs.execute(sql_cmd, data)
                        res = curs.fetchone()
                        if res[0] and res[0].strip():
                            user_name = res[0]

                        # Create user and send Welcome message
                        self.add_new_user(user_name, user_email)
                        c.send_email(self.queues["sender"], user_email, "", "Welcome", \
                                     "", "", message_id)
                    else:
                    # After Registration deadline
                        c.send_email(self.queues["sender"], user_email, "", "RegOver", \
                                     "", "", message_id)
            else:
            # Not on Whitelist
                c.send_email(self.queues["sender"], user_email, "", "NotAllowed", \
                             "", "", message_id)

        cons.close()

    ####
    # loop_code
    ####
    def loop_code(self):
        """
        The code run in the while True loop of the mail fetcher thread.
        """

        m = self.connect_to_imapserver()

        if m != 0:
            self.handle_backlogged(m)
            self.handle_new(m)
            self.archive_processed(m)
            self.disconnect_from_imapserver(m)

        time.sleep(self.poll_period)

    ####
    # run
    ####
    def run(self):
        """
        Thread code for the fetcher thread.
        """

        c.log_a_msg(self.queues["logger"], self.name, "Starting Mail Fetcher Thread!", "INFO")

        logmsg = "Imapserver: '" + self.imap_info["server"] + "'"
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        # This thread is running as a daemon thread, this is the while(1) loop that is
        # running until the thread is stopped by the main thread
        while True:
            self.loop_code()

        logmsg = "Exiting fetcher - this should NEVER happen!"
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
