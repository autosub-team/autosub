#######################################################################
# sender.py -- send out e-mails based on the info given by fetcher.py
#       or worker.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################
"""
Only one thread is in charge of sending out e-mails.
"""

import threading
import smtplib, os, time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sqlite3 as lite
import common as c

class MailSender(threading.Thread):
    """
    Thread in charge of sending out mails (responses to users as well as
    notifications for admins).
    """
    def __init__(self, name, sender_queue, autosub_mail, autosub_user, \
                 autosub_passwd, autosub_smtpserver, logger_queue, arch_queue, \
                 coursedb, semesterdb):
        threading.Thread.__init__(self)
        self.name = name
        self.sender_queue = sender_queue
        self.autosub_user = autosub_user
        self.mail_user = autosub_mail
        self.mail_pwd = autosub_passwd
        self.smtpserver = autosub_smtpserver
        self.logger_queue = logger_queue
        self.arch_queue = arch_queue
        self.coursedb = coursedb
        self.semesterdb = semesterdb

####
# get_admin_emails()
####
    def get_admin_emails(self):
        """
        read e-mail adress(es) of adminstrator(s) from DB.
        """
        curc, conc = c.connect_to_db(self.coursedb, \
                                     self.logger_queue, \
                                     self.name)

        sql_cmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'admin_email'"
        curc.execute(sql_cmd)
        result = str(curc.fetchone()[0])
         #split and put it in list
        admin_emails = [email.strip() for email in result.split(',')]
        conc.close()

        return admin_emails

####
# increment_db_taskcounter()
####
    def increment_db_taskcounter(self, curs, cons, countername, tasknr):
        """
        the taskcounters are used to keep track for each task how many
        users have solved that task successfully
        """
        data = {'cname': countername, 'tasknr': tasknr}
        sql_cmd = "UPDATE TaskStats SET {0} =(SELECT :cname FROM TaskStats WHERE TaskId == :tasknr)+1 WHERE TaskId == :tasknr".format(countername)
        curs.execute(sql_cmd, data)
        cons.commit()

####
# check_and_set_last_done()
#
# Check if the timestamp in lastDone has been set. If so, leave the old one
# as we want to know when the user submitted the correct version of the last
# task for the very first time.
# If this is the first time, write the current timestamp into the database.
####
    def check_and_set_last_done(self, curs, cons, userid):
        """
        The LastDone flag is used to mark users who have successfully solved
        all tasks.
        """
        data = {'uid': userid}
        sql_cmd = "SELECT LastDone FROM Users WHERE UserId == :uid;"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        logmsg = "RES: "+ str(res[0])
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        if str(res[0]) == 'None':
            data = {'uid': str(userid), 'now': str(int(time.time()))}
            sql_cmd = "UPDATE Users SET LastDone = datetime(:now, 'unixepoch', 'localtime') WHERE UserId == :uid;"
            curs.execute(sql_cmd, data)
            cons.commit()

####
# check_and_set_first_successful
#
# set FirstSuccessful to last submission if not set yet
####
    def check_and_set_first_successful(self, curs, cons, uid, tasknr):
        """
        the FirstSuccessful field is used to keep track on how many attempts
        were needed to solve a task.
        """

        # check if allready previous successful submission, if not set it
        data = {'uid': uid, 'tasknr': tasknr}
        sql_cmd = "SELECT FirstSuccessful FROM UserTasks WHERE UserId = :uid AND TaskNr = :tasknr;"
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        if res[0] == None:
            # get last submission number
            sql_cmd = "SELECT NrSubmissions FROM UserTasks WHERE UserId = :uid AND TaskNr = :tasknr;"
            curs.execute(sql_cmd, data)
            res = curs.fetchone()
            submission_nr = int(res[0])
            # set first successful
            data['subnr'] = submission_nr
            sql_cmd = "UPDATE UserTasks SET FirstSuccessful = :subnr WHERE UserId = :uid AND TaskNr = :tasknr;"
            curs.execute(sql_cmd , data)
            cons.commit()

####
# read_specialmessage
#
####
    def read_specialmessage(self, msgname):
        """
        read a special message from the DB
        """
        curc, conc = c.connect_to_db(self.coursedb, \
                                     self.logger_queue, \
                                     self.name)

        data = {'msgname': msgname}
        sql_cmd = "SELECT EventText FROM SpecialMessages WHERE EventName = :msgname;"
        curc.execute(sql_cmd, data)
        res = curc.fetchone()
        conc.close()
        return str(res[0])

####
# generate_status_update()
####
    def generate_status_update(self, curs, user_email):
        """
        generate the e-mail body for response to a status mail
        """
        data = {'user_email': user_email}
        sql_cmd = "SELECT Name FROM Users WHERE Email = :user_email;"
        curs.execute(sql_cmd, data)
        uname = curs.fetchone()
        sql_cmd = "SELECT CurrentTask FROM Users WHERE Email = :user_email;"
        curs.execute(sql_cmd, data)
        curtask = curs.fetchone()

        conc = lite.connect(self.coursedb)
        curc = conc.cursor()
        data = {'curtask': str(curtask[0])}
        sql_cmd = "SELECT SUM(Score) FROM TaskConfiguration WHERE TaskNr < :curtask;"
        curc.execute(sql_cmd, data)
        curscore = curc.fetchone()
        curc.close()

        if str(curscore[0]) == 'None': # no task solved yet.
            tmpscore = 0
        else:
            tmpscore = curscore[0]

        msg = "Username: {0}\nEmail: {1}\nCurrent Task: {2}\n Your current Score: {3}\n".format(str(uname[0]), user_email, str(curtask[0]), str(tmpscore))

        try:
            cur_deadline = c.get_task_deadline(self.coursedb, str(curtask[0]), \
                                               self.logger_queue, self.name)
            cur_start = c.get_task_starttime(self.coursedb, str(curtask[0]), \
                                             self.logger_queue, self.name)

            msg = "{0}\nStarttime current Task: {1}\n".format(msg, cur_start)
            msg = "{0}Deadline current Task: {1}".format(msg, cur_deadline)
        except:
            msg = "{0}\nNo more deadlines for you -- all Tasks are finished!".format(msg)

        return msg

####
# backup_message()
#
# Just a stub, in the future, the message with the messageid shall be moved
# into an archive folder on the mailserver.
####
    def backup_message(self, messageid):
        """
        trigger  archivation of an e-mail
        """
        logmsg = "request backup of message with messageid: {0}".format(messageid)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        self.arch_queue.put(dict({"mid": messageid}))

    def send_out_email(self, recipient, message, msg_type):
        """
        connect to the smtp server and send out an e-mail
        """
        try:
            # port 465 doesn't seem to work!
            server = smtplib.SMTP(self.smtpserver, 587)
            server.ehlo()
            server.starttls()
            server.login(self.autosub_user, self.mail_pwd)
            server.sendmail(self.mail_user, recipient, message)
            server.close()
            c.log_a_msg(self.logger_queue, self.name, "Successfully sent an e-mail of type '{0}'!".format(msg_type), "DEBUG")
            c.increment_db_statcounter(self.semesterdb, 'nr_mails_sent', \
                                       self.logger_queue, self.name)
        except:
            c.log_a_msg(self.logger_queue, self.name, "Failed to send out an e-mail of type '{0}'!".format(msg_type), "ERROR")

    def read_text_file(self, path_to_msg):
        """
        read a text file
        """
        try:
            fpin = open(path_to_msg, 'r')
            message_text = fpin.read()
            fpin.close()
        except:
            message_text = "Even the static file was not available!"
            c.log_a_msg(self.logger_queue, self.name, \
                        "Failed to read from config file", "WARNING")

        return message_text

    def assemble_email(self, msg, message_text, attachments):
        """
        assemble e-mail content
        """
        msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

        # If the message is a task description, we might want to
        # add some attachments.  These ar given as a list by the
        # attachments parameter
        logmsg = "List of attachements: {0}".format(attachments)
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        if str(attachments) != 'None':
            for next_attachment in attachments:
                try:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(open(next_attachment, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(next_attachment)))
                    msg.attach(part)
                except:
                    logmsg = "Faild to add an attachement: {0}".format(next_attachment)
                    c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        # The following message my be helpful during debugging - but
        # if you use attachments, your log-file will grow very fast
        # therefore it was commented out.
#        logmsg = "Prepared message: \n" + str(msg)
#        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
        return msg

    def handle_next_mail(self):
        """
        parse the subject/content of a mail and take appropriate action.
        """
        #blocking wait on sender_queue
        next_send_msg = self.sender_queue.get(True)

        tasknr = str(next_send_msg.get('Task'))
        messageid = str(next_send_msg.get('MessageId'))
        uid = str(next_send_msg.get('UserId'))
        recipient = str(next_send_msg.get('recipient'))
        message_type = str(next_send_msg.get('message_type'))

        curs, cons = c.connect_to_db(self.semesterdb, self.logger_queue, \
                                     self.name)
        curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, \
                                     self.name)

        attachments = []

        # prepare fields for the e-mail
        msg = MIMEMultipart()
        msg['From'] = self.mail_user
        msg['To'] = recipient
        logmsg = "RECIPIENT: " + recipient
        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

        msg['Date'] = formatdate(localtime=True)

        if message_type == "Task":
            logmsg = "Task in send_queue: " + str(next_send_msg)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            numtasks = c.get_num_tasks(self.coursedb, \
                       self.logger_queue, self.name)
            ctasknr = c.user_get_current_task(self.semesterdb, uid, \
                                             self.logger_queue, self.name)
            if numtasks+1 == int(tasknr): # last task solved!
                msg['Subject'] = "Congratulations!"
                message_text = self.read_specialmessage('CONGRATS')

                if int(tasknr)-1 == int(ctasknr):
                    # statistics shall only be udated on the first
                    # successful submission
                    c.user_set_current_task(self.semesterdb, tasknr, uid, \
                                           self.logger_queue, self.name)
                    self.increment_db_taskcounter(curs, cons, 'NrSuccessful', \
                                                  str(int(tasknr)-1))
                    self.increment_db_taskcounter(curs, cons, 'NrSubmissions', \
                                                  str(int(tasknr)-1))
                    self.check_and_set_last_done(curs, cons, uid)

                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(recipient, msg.as_string(), message_type)
            else: # at least one more task to do: send out the description
                # only send the task description, after the first
                # successful submission
                if int(tasknr)-1 <= int(ctasknr) or int(ctasknr) == 1:
                    msg['Subject'] = "Description Task" + str(tasknr)

                    dl_text = "\nDeadline for this Task: {0}\n".format(c.get_task_deadline(self.coursedb, tasknr, self.logger_queue, self.name))

                    data = {'tasknr': str(tasknr)}
                    sql_cmd = "SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == :tasknr;"
                    curc.execute(sql_cmd, data)
                    paths = curc.fetchone()

                    if not paths:
                        logmsg = "It seems, the Path to Task {0} is not configured.".format(tasknr)
                        c.log_a_msg(self.logger_queue, self.name, \
                                    logmsg, "WARNING")

                        message_text = "Sorry, but something went wrong... probably misconfiguration or missing configuration of Task {0}".format(tasknr)
                        msg = self.assemble_email(msg, message_text, '')
                        self.send_out_email(recipient, msg.as_string(), \
                                            message_type)
                    else:
                        path_to_task = str(paths[0])
                        path_to_msg = path_to_task + "/description.txt"
                        message_text = self.read_text_file(path_to_msg) \
                                       + dl_text

                        data = {'tasknr': str(tasknr), 'uid': uid}
                        sql_cmd = "SELECT TaskAttachments FROM UserTasks WHERE TaskNr == :tasknr AND UserId == :uid;"
                        curs.execute(sql_cmd, data)
                        res = curs.fetchone()

                        logmsg = "got the following attachments: " + str(res)
                        c.log_a_msg(self.logger_queue, self.name, logmsg, \
                                    "DEBUG")
                        if res:
                            attachments = str(res[0]).split()

                        # statistics shall only be udated on the first
                        # succesful submission
                        c.user_set_current_task(self.semesterdb, tasknr, uid, \
                                               self.logger_queue, self.name)
                        self.increment_db_taskcounter(curs, cons, \
                                                      'NrSuccessful', \
                                                      str(int(tasknr)-1))
                        self.increment_db_taskcounter(curs, cons, \
                                                      'NrSubmissions', \
                                                      str(int(tasknr)-1))

                        msg = self.assemble_email(msg, message_text, \
                                                  attachments)
                        self.send_out_email(recipient, msg.as_string(), \
                                            message_type)

            self.backup_message(messageid)

        elif message_type == "Failed":
            self.increment_db_taskcounter(curs, cons, 'NrSubmissions', tasknr)
            path_to_msg = "users/{0}/Task{1}".format(uid, tasknr)
            error_msg = self.read_text_file("{0}/error_msg".format(path_to_msg))
            msg['Subject'] = "Task" + tasknr + ": submission rejected"
            message_text = "Error report:\n\n""" + error_msg

            reply_attachments = []

            try:
                logmsg = "searching attachments in: {0}/error_attachments".format(path_to_msg)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                ats = os.listdir("{0}/error_attachments".format(path_to_msg))
                logmsg = "got the following attachments: {0}".format(ats)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                for next_attachment in ats:
                    reply_attachments.append("{0}/error_attachments/{1}".format(path_to_msg, next_attachment))
            except:
                logmsg = "no attachments for failed task."
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

            msg = self.assemble_email(msg, message_text, reply_attachments)
            self.send_out_email(recipient, msg.as_string(), message_type)
            self.backup_message(messageid)

        elif message_type == "SecAlert":
            admin_mails = self.get_admin_emails()
            for admin_mail in admin_mails:
                msg['To'] = admin_mail
                path_to_msg = "users/"+ uid + "/Task" + tasknr + "/error_msg"
                error_msg = self.read_text_file(path_to_msg)
                msg['Subject'] = "Autosub Security Alert User:" + recipient
                message_text = "Error report:\n\n""" + error_msg
                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(admin_mail, msg.as_string(), message_type)
                self.backup_message(messageid)

        elif message_type == "TaskAlert":
            admin_mails = self.get_admin_emails()
            for admin_mail in admin_mails:
                msg['To'] = admin_mail
                msg['Subject'] = "Autosub Task Error Alert Task " \
                                 + tasknr + " User " + uid
                message_text = "Something went wrong with task/testbench analyzation for Task " + tasknr +" and User " + uid + " . Either the entity or testbench analyzation threw an error."
                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(admin_mail, msg.as_string(), message_type)
                self.backup_message(messageid)

        elif message_type == "Success":
            msg['Subject'] = "Task " + tasknr + " submitted successfully"
            message_text = "Congratulations!"
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
            #set first done if not set yet
            self.check_and_set_first_successful(curs, cons, uid, tasknr)

            # no backup of message -- this is done after the new task
            # description was sent to the user!
        elif message_type == "Status":
            msg['Subject'] = "Your Current Status"
            message_text = self.generate_status_update(curs, recipient)
            numtasks = c.get_num_tasks(self.coursedb, self.logger_queue, \
                                       self.name)
            if int(numtasks) >= int(tasknr):
                #also attach current task
                data = {'tasknr': str(tasknr), 'uid': uid}
                sql_cmd = "SELECT TaskAttachments FROM UserTasks WHERE TaskNr == :tasknr AND UserId == :uid;"
                curs.execute(sql_cmd, data)
                res = curs.fetchone()
                logmsg = "got the following attachments: " + str(res)
                c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                if res:
                    attachments = str(res[0]).split()
                msg = self.assemble_email(msg, message_text, attachments)
                self.send_out_email(recipient, msg.as_string(), message_type)
            else:
                msg = self.assemble_email(msg, message_text, attachments)
                self.send_out_email(recipient, msg.as_string(), message_type)

            self.backup_message(messageid)

        elif message_type == "InvalidTask":
            msg['Subject'] = "Invalid Task Number"
            message_text = self.read_specialmessage('INVALID')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "CurLast":
            # we still need to increment the users task counter!
            c.user_set_current_task(self.semesterdb, tasknr, uid, \
                                   self.logger_queue, self.name)
            msg['Subject'] = "Task{0} is not available yet".format(str(tasknr))
            message_text = self.read_specialmessage('CURLAST')
            message_text = "{0}\n\nThe Task is currently scheduled for: {1}".format(message_text, \
                   c.get_task_starttime(self.coursedb, str(tasknr), \
                   self.logger_queue, self.name))
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "DeadTask":
            msg['Subject'] = "Deadline for Task{0} has passed.".format(str(tasknr))
            message_text = self.read_specialmessage('DEADTASK')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "Usage":
            msg['Subject'] = "Autosub Usage"
            message_text = self.read_specialmessage('USAGE')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "Question":
            msg['Subject'] = "Question received"
            message_text = self.read_specialmessage('QUESTION')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "QFwd":
            orig_mail = next_send_msg.get('Body')
            msg['Subject'] = "Question from " + orig_mail['from']

            if orig_mail.get_content_maintype() == 'multipart':
                part = orig_mail.get_payload(0)
                mbody = part.get_payload()
                message_text = "Original subject: " + orig_mail['subject'] + "\n\nNote: This e-mail contained attachments which have been removed!\n"
                message_text = "{0}\n\nOriginal body:\n{1}".format(message_text, mbody)
            else:
                mbody = orig_mail.get_payload()
                message_text = "Original subject: " + orig_mail['subject'] + \
                       "\n\nOriginal body:\n" + str(mbody)

            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "Welcome":
            msg['Subject'] = "Welcome!"
            message_text = self.read_specialmessage('WELCOME')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "RegOver":
            msg['Subject'] = "Registration Deadline has passed"
            message_text = self.read_specialmessage('REGOVER')
            self.backup_message(messageid)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
        elif message_type == "NotAllowed":
            msg['Subject'] = "Registration Not Successful."
            message_text = self.read_specialmessage('NOTALLOWED')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
            self.backup_message(messageid)
        else:
            c.log_a_msg(self.logger_queue, self.name, \
                        "Unkown Message Type in the sender_queue!", "ERROR")
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type)
            self.backup_message(messageid)

        cons.close()
        conc.close()

####
# thread code of the sender thread.
####
    def run(self):
        """
        the thread code is just a tight loop that waits on the sender_queue
	for some work.
        """
        c.log_a_msg(self.logger_queue, self.name, \
                    "Starting Mail Sender Thread!", "INFO")

        while True:
            self.handle_next_mail()
