########################################################################
# fetcher.py -- fetch e-mails from the mailbox
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck    <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import email
import imaplib
import os
import time
import re #regex
import datetime
import common as c

class mailFetcher(threading.Thread):
    """
    Thread in charge of fetching emails from IMAP and based on these emails
    assigns work to other threads.
    """

    def __init__(self, threadID, name, job_queue, sender_queue, gen_queue, imapuser, \
                 imappasswd, imapserver, imapport, imapsecurity, logger_queue, arch_queue, \
                 poll_period, coursedb, semesterdb, allow_skipping):
        """
        Constructor for fetcher thread
        """

        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.job_queue = job_queue
        self.sender_queue = sender_queue
        self.gen_queue = gen_queue
        self.imap_user = imapuser
        self.imap_pwd = imappasswd
        self.imap_server = imapserver
        self.imap_port = imapport
        self.imap_security = imapsecurity
        self.logger_queue = logger_queue
        self.arch_queue = arch_queue
        self.poll_period = poll_period
        self.coursedb = coursedb
        self.semesterdb = semesterdb
        self.allow_skipping = allow_skipping

    ####
    # get_admin_emails
    ####
    def get_admin_emails(self):
        """
        Get the email adresses of all configured admins.

        Return a list.
        """

        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

        sql_cmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'admin_email'"
        curc.execute(sql_cmd)
        result = curc.fetchone()
        if result != None:
            result = str(result[0])
            admin_emails = [email.strip() for email in result.split(',')]
        else:
            admin_emails = ""

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

        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

        data = {'TaskNr': task_nr}
        sql_cmd = "SELECT TaskOperator FROM TaskConfiguration WHERE TaskNr = :TaskNr"
        curc.execute(sql_cmd, data)
        result = curc.fetchone()
        if result != None:
            result = str(result[0])
            taskoperator_emails = [email.strip() for email in result.split(',')]
        else:
            taskoperator_emails = ""

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

        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

        logmsg = 'Creating new Account: User: %s' % user_name
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

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
        if res == None:
            logmsg = ("Creating new user with "
                      "name= {0} , email={1} failed").format(user_name, user_email)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        user_id = str(res[0])
        dir_name = 'users/'+ user_id
        c.check_dir_mkdir(dir_name, self.logger_queue, self.name)

        cons.close()

        # generate task 1 for user
        logmsg = ("Calling Generator to create"
                  "TaskNr:{0} for UserId:{1}").format(1, user_id)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        self.gen_queue.put(dict({"user_id": user_id, "user_email": user_email, \
                           "task_nr": "1", "messageid": ""}))

    ###
    # increment_submission_nr
    ##
    def increment_submission_nr(self, user_id, task_nr):
        """
        Increment submission number for a specific user and task.

        Return new number or 0 if no previous submission for this task exists.
        """

        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

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
    def save_submission_user_dir(self, user_email, task_nr, mail, messageid):
        """
        Store a new submisson in the user's directory structure.
        """
        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

        data = {'Email': user_email}
        sql_cmd = "SELECT UserId FROM Users WHERE Email = :Email"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        user_id = res[0]

        # increment the submission_nr for the user
        submission_nr = self.increment_submission_nr(int(user_id), int(task_nr))

        #create a directory for putting his submission in:
        detach_dir = 'users/{0}/Task{1}'.format(user_id, task_nr)
        ts = datetime.datetime.now()
        submission_dir = "/Submission{0}_{1}{2}{3}_{4}{5}{6}{7}".format(\
            submission_nr, ts.year, ts.month, ts.day, ts.hour, ts.minute, \
            ts.second, ts.microsecond)
        current_dir = detach_dir + submission_dir
        c.check_dir_mkdir(current_dir, self.logger_queue, self.name)

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

            # if there is no filename, create one with a counter to avoid duplicates
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

        cons.close()

    ####
    # get_archive_dir
    ###
    def get_archive_dir(self):
        """
        Get the  name of the directory processed mails shall be moved to
        on the IMAP server
        """

        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)

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
    def a_question_was_asked(self, user_id, user_email, mail, messageid):
        """
        Process a question that was asked by a user.
        """

        mail_subject = str(mail['subject'])

        logmsg = 'The user has a question, please take care of that!'
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
        c.send_email(self.sender_queue, user_email, "", "Question", "", "", "")

        # was the question asked to a specific task_nr that is valid?
        search_obj = re.search('[0-9]+', mail_subject, )

        if (search_obj != None) and int(search_obj.group()) <= c.get_num_tasks(self.coursedb, \
                                            self.logger_queue, self.name):
            tasknr = search_obj.group()
            fwd_mails = self.get_taskoperator_emails(tasknr)
            if fwd_mails == "":
                logmsg = ("Error getting the taskoperator email for task {0}. "
                          "Question from user with email={1} "
                          "dropped.").format(tasknr, user_email)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                return
        else:
            fwd_mails = self.get_admin_emails()
            if fwd_mails == "":
                logmsg = ("Error getting the admin email for task {0}. "
                          "Question from user with email={1} "
                          "dropped.").format(tasknr, user_email)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                return

        for mail_address in fwd_mails:
            c.send_email(self.sender_queue, mail_address, user_id, "QFwd", "", mail, messageid)

        c.increment_db_statcounter(self.semesterdb, 'nr_questions_received', \
                                   self.logger_queue, self.name)


    ####
    # a_status_is_requested
    ####
    def a_status_is_requested(self, user_id, user_email, messageid):
        """
        Tell sender to send out a status email.
        """
        logmsg = ("STATUS requested: User with UserId:{0}, Email: {1}").format(\
                 user_id, user_email)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")


        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

        data = {'user_id':user_id}
        sql_cmd = "SELECT CurrentTask FROM Users WHERE UserId == :user_id"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        current_task = res[0]

        cons.close()

        c.send_email(self.sender_queue, user_email, user_id, "Status", current_task, \
                     "", messageid)
        c.increment_db_statcounter(self.semesterdb, 'nr_status_requests', \
                                   self.logger_queue, self.name)

    ####
    # a_result_was_submitted
    ####
    def a_result_was_submitted(self, user_id, user_email, task_nr, messageid, \
                               mail):
        logmsg = "Processing a Result, UserId:{0} TaskNr:{1}"\
                .format(user_id, task_nr)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        # at which task_nr is the user
        cur_task = c.user_get_current_task(self.semesterdb, user_id, self.logger_queue, \
                                      self.name)

        #task with this tasknr exists?
        is_task = c.is_valid_task_nr(self.coursedb, task_nr, self.logger_queue,\
                                     self.name)

        if is_task == False:
        # task_nr is not valid
            c.send_email(self.sender_queue, user_email, "", "InvalidTask", str(task_nr), \
                         "", messageid)
            return

        # task_nr is valid, get deadline
        deadline = c.get_task_deadline(self.coursedb, task_nr, self.logger_queue, \
                                           self.name)

        if is_task and cur_task < int(task_nr):
        #task_nr valid, but user has not reached that tasknr yet
            logmsg = ("User can not submit for this task yet.")
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

            c.send_email(self.sender_queue, user_email, "", "TaskNotSubmittable", str(task_nr), \
                         "", messageid)

        elif deadline < datetime.datetime.now():
        # deadline passed for that task_nr!
            logmsg = ("Deadline passed")
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

            c.send_email(self.sender_queue, user_email, "", "DeadTask", str(task_nr), \
                         "", messageid)

        else:
        # okay, let's work with the submission

            #save the attached files to user task directory
            self.save_submission_user_dir(user_email, task_nr, mail, messageid)

            # send job request to worker
            self.job_queue.put(dict({"UserId": user_id, "UserEmail": user_email, \
                               "message_type": "Task", "taskNr": task_nr, \
                               "MessageId": messageid}))

    ####
    # skip_was_requested
    ####
    def skip_was_requested(self, user_id, user_email, messageid):
         # at which task_nr is the user
        cur_task = c.user_get_current_task(self.semesterdb, user_id, self.logger_queue, \
                                           self.name)
        next_task = cur_task + 1

        logmsg = ("Skip requested: User with UserId:{0}, from "
                  "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        #task with this tasknr exists?
        is_task = c.is_valid_task_nr(self.coursedb, next_task, self.logger_queue,\
                                     self.name)
        if is_task == True:
            task_starttime = c.get_task_starttime(self.coursedb, next_task,
                                                  self.logger_queue, self.name)
            task_has_started = task_starttime < datetime.datetime.now()

            if task_has_started == True:
                #set new current task
                c.user_set_current_task(self.semesterdb, next_task, user_id, \
                                        self.logger_queue, self.name)
                #tell generator thread to create new task
                logmsg = ("Calling Generator to create "
                          "TaskNr:{0} for UserId:{1}").format(next_task, user_id)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                self.gen_queue.put(dict({"user_id": user_id, "user_email": user_email, \
                           "task_nr": next_task, "messageid": messageid}))

                logmsg = ("Skip done: User with UserId:{0}, from "
                          "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

                return

        #Skip not possible
        logmsg = ("Skip NOT POSSIBLE: User with UserId:{0}, from "
                  "TaskNr= {1} to {2}").format(user_id, cur_task, next_task)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        c.send_email(self.sender_queue, user_email, "", "SkipNotPossible", \
                     "", "", messageid)

    ####
    # connect_to_imapserver
    ####
    def connect_to_imapserver(self):
        """
        Connect to configured IMAP server.
        """

        try:
            # connecting to the imap server
            if self.imap_security == 'ssl':
                server = imaplib.IMAP4_SSL(self.imap_server, int(self.imap_port))
            else:
                server = imaplib.IMAP4(self.imap_server, int(self.imap_port))

            if self.imap_security == 'starttls':
                server.starttls()

            server.login(self.imap_user, self.imap_pwd)
        except imaplib.IMAP4.abort:
            logmsg = "Login to server was aborted with security= " + self.imap_security + \
                     " , port= " + str(self.imap_port)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            #m.close()
            return 0
        except imaplib.IMAP4.error:
            logmsg = "Got an error when trying to connect to the imap server with" + \
                     " security= " + self.imap_security + " , port= " + str(self.imap_port)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            return 0
        except:
            logmsg = "Got an unknown exception when trying to connect to the imap " + \
                     "server with security= " + self.imap_security + " , port= " + str(self.imap_port)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            return 0

        logmsg = "Successfully logged into imap server with security= " + self.imap_security + \
                 " , port= " + str(self.imap_port)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        return server

    ####
    # fetch_new_emails
    ####
    def fetch_new_emails(self, m):
        """
        Fetch new (unseen e-mails from the Inbox.

        Return list of mailids
        """

        try:
            m.select("Inbox") # here you a can choose a mail box like INBOX instead
            # use m.list() to get all the mailboxes
        except:
            logmsg = "Failed to select inbox"
            c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
            return []

        # you could filter using the IMAP rules here
        # (check http://www.example-code.com/csharp/imap-search-critera.asp)
        resp, items = m.search(None, "UNSEEN")
        return items[0].split()

    def fetch_all_emails(self, m):
        """
        Fetch all emails.

        Return list of mailids.
        """

        try:
            m.select(mailbox='Inbox', readonly=False)
        except:
            logmsg = "Failed to select inbox"
            c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
            return []

        resp, items = m.search(None, 'All')
        return items[0].split()

    ####
    # check_if_whitelisted
    ####
    def check_if_whitelisted(self, user_email):
        """
        Check if the given e-mail address is in the whitelist.
        """

        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)

        data = {'Email': user_email}
        sql_cmd = "SELECT * FROM WhiteList WHERE Email == :Email"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()

        cons.close()

        if res != None:
            return 1
        else:
            logmsg = "Got Mail from a User not on the WhiteList: " + user_email
            c.log_a_msg(self.logger_queue, self.name, logmsg, "Warning")
            c.increment_db_statcounter(self.semesterdb, 'nr_non_registered', \
                                       self.logger_queue, self.name)

            return 0

    ####
    # get_registration_deadline
    ####
    def get_registration_deadline(self):
        """
        Get the registration deadline datetime.

        Return datetime, if not found return 1 hour from now.
        """

        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)
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
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

            return date

    ####
    # action_by_subject
    ####
    def action_by_subject(self, user_id, user_email, messageid, mail, mail_subject):

        if re.search('[Rr][Ee][Ss][Uu][Ll][Tt]', mail_subject):
        ###############
        #   RESULT    #
        ###############
            searchObj = re.search('[0-9]+', mail_subject)
            if searchObj == None:
            # Result + no number
                logmsg = ("Got a kind of message I do not understand. "
                          "Sending a usage mail...")
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                c.send_email(self.sender_queue, user_email, "", "Usage", "", \
                             "", messageid)
                return

            #Result + number
            task_nr = searchObj.group()

            self.a_result_was_submitted(user_id, user_email, task_nr, messageid, \
                                        mail)

        elif re.search('[Qq][Uu][Ee][Ss][Tt][Ii][Oo][Nn]', mail_subject):
        ###############
        #   QUESTION  #
        ###############
            self.a_question_was_asked(user_id, user_email, mail, messageid)

        elif re.search('[Ss][Tt][Aa][Tt][Uu][Ss]', mail_subject):
        ###############
        #   STATUS    #
        ###############
            self.a_status_is_requested(user_id, user_email, messageid)

        elif (self.allow_skipping == True) and re.search('[Ss][Kk][Ii][Pp]', mail_subject):
        ####################
        # SKIP, IF ALLOWED #
        ####################
            self.skip_was_requested(user_id, user_email, messageid)

        else:
        #####################
        #   DEFAULT ACTION  #
        #####################
            logmsg = ("Got a kind of message I do not understand. "
                      "Sending a usage mail...")
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            c.send_email(self.sender_queue, user_email, "", "Usage", "", \
                         "", messageid)
    ####
    # loop_code
    ####
    def loop_code(self):
        """
        The code run in the while True loop of the mail fetcher thread.
        """

        m = self.connect_to_imapserver()

        if m != 0:
            curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)
            items = self.fetch_new_emails(m)

            # iterate over all new e-mails and take action according to the structure
            # of the subject line
            for emailid in items:

                c.increment_db_statcounter(self.semesterdb, 'nr_mails_fetched', \
                                           self.logger_queue, self.name)

                # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you
                # can ask for headers only, etc
                resp, data = m.fetch(emailid, "(RFC822)")

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

                messageid = mail.get('Message-ID')

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
                                  "(UserId:{0}, Email:{1}").format(user_id,
                                  user_email)
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                        # Take action based on the subject
                        self.action_by_subject(user_id, user_email, messageid, mail, \
                                          mail_subject)

                    else:
                    # Not yet registered
                        reg_deadline = self.get_registration_deadline()

                        if reg_deadline > datetime.datetime.now():
                        # Before Registraton deadline
                            self.add_new_user(user_name, user_email)
                            c.send_email(self.sender_queue, user_email, "", "Welcome", \
                                         "", "", messageid)
                        else:
                        # After Registration deadline
                            c.send_email(self.sender_queue, user_email, "", "RegOver", \
                                         "", "", messageid)
                else:
                # Not on Whitelist
                    c.send_email(self.sender_queue, user_email, "", "NotAllowed", \
                                 "", "", messageid)

            try:
                m.close()
            except imaplib.IMAP4.abort:
                logmsg = ("Closing connection to server was aborted "
                          "(probably a server-side problem). Trying to connect again ...")
                c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
                #m.close()
            except imaplib.IMAP4.error:
                logmsg = ("Got an error when trying to connect to the imap server."
                          "Trying to connect again ...")
                c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            except:
                logmsg = ("Got an unknown exception when trying to connect to the "
                          "imap server. Trying to connect again ...")
                c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            finally:
                logmsg = "closed connection to imapserver"
                c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")


            # check if messages have been handled and need to be archived now
            try:
                next_send_msg = self.arch_queue.get(False)
            except:
                next_send_msg = 'NONE'

            if next_send_msg != 'NONE':
                c.log_a_msg(self.logger_queue, self.name, "moving a message!!!!!!!", \
                            "INFO")
                m = self.connect_to_imapserver()
                archive_dir = self.get_archive_dir()

                for next_msg in next_send_msg:
                    email_ids = self.fetch_all_emails(m)

                    for emailid in email_ids:
                        typ, msg_data = m.fetch(str(int(emailid)), "(BODY[HEADER])")
                        mail = email.message_from_bytes(msg_data[0][1])
                        if mail['Message-ID'] == next_send_msg.get('mid'):
                            logmsg = "Moving Message with ID: {0}"\
                                     .format(mail['Message-ID'])
                            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

                            resp, data = m.fetch(emailid, "(UID)")
                            pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')
                            match = pattern_uid.match(str(data[0]).split("'")[1])
                            msg_uid = match.group('uid')

                            result = m.uid('COPY', msg_uid, archive_dir)

                            if result[0] == 'OK':
                                mov, data = m.uid('STORE', msg_uid, '+FLAGS', \
                                                  '(\Deleted)')
                                m.expunge()
                            else:
                                log_msg = ("Error moving a message. Is the "
                                    "configured archive_dir '{0}' existing "
                                    "on the IMAP server?!").format(archive_dir)
                                c.log_a_msg(self.logger_queue, self.name, \
                                    log_msg, "ERROR")
                            break

                # m==0 is only possible in test-code (e.g. load_test.py)
                if m != 0:
                    m.logout()

            cons.close()

        time.sleep(self.poll_period)

    ####
    # run
    ####
    def run(self):
        """
        Thread code for the fetcher thread.
        """

        c.log_a_msg(self.logger_queue, self.name, "Starting Mail Fetcher Thread!", "INFO")

        logmsg = "Imapserver: '" + self.imap_server + "'"
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        # This thread is running as a daemon thread, this is the while(1) loop that is
        # running until the thread is stopped by the main thread
        while True:
            self.loop_code()

        logmsg = "Exiting fetcher - this should NEVER happen!"
        c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

