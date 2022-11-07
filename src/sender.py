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
import smtplib
import os
import time
import json

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

import common as c

class MailSender(threading.Thread):
    """
    Thread in charge of sending out mails (responses to users as well as
    notifications for admins).
    """
    def __init__(self, name, queues, dbs, smtp_info, course_info, allow_requests):
        """
        Constructor for sender thread
        """

        threading.Thread.__init__(self)
        self.name = name
        self.queues = queues
        self.dbs = dbs
        self.smtp_info = smtp_info
        self.course_info = course_info
        self.allow_requests = allow_requests

####
# get_admin_emails
####
    def get_admin_emails(self):
        """
        read e-mail adress(es) of adminstrator(s) from DB.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], \
                                     self.queues["logger"], \
                                     self.name)

        sql_cmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'admin_email'"
        curc.execute(sql_cmd)
        result = str(curc.fetchone()[0])
        #split and put it in list
        admin_emails = [email.strip() for email in result.split(',')]
        conc.close()

        return admin_emails

####
# increment_db_taskcounter
####
    def increment_db_taskcounter(self, countername, task_nr):
        """
        the taskcounters are used to keep track for each task how many
        users have solved that task successfully
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], \
                                     self.name)

        data = {'task_nr': task_nr}
        # SET with parameter does not work --> string substitute here
        sql_cmd = ("UPDATE TaskStats SET {0} = {0} + 1 "
                   "WHERE TaskId == :task_nr").format(countername)
        curs.execute(sql_cmd, data)
        cons.commit()
        cons.close()

####
# has_last_done
####
    def has_last_done(self, userid):
        """
        Has the user a date in the LastDone field?
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], \
                                     self.name)

        data = {'user_id': userid}
        sql_cmd = ("SELECT UserId FROM Users "
                   "WHERE UserId == :user_id AND LastDone IS NOT NULL")
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        last_done = (res != None)
        cons.close()

        return last_done

####
# check_and_set_last_done
####
    def check_and_set_last_done(self, userid):
        """
        The LastDone field is used to mark users who have successfully solved
        all tasks.

        Returns: If the LastDone had to be set right now
        """

        #has he already last done? --> nothing to do
        if self.has_last_done(userid):
            return False

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], \
                                     self.name)

        #get number of successful tasks
        data = {'user_id': userid}
        sql_cmd = ("SELECT COUNT(*) FROM SuccessfulTasks "
                   "WHERE UserId = :user_id")
        curs.execute(sql_cmd, data)
        count_successful = curs.fetchone()[0]

        num_tasks = c.get_num_tasks(self.dbs["course"], self.queues["logger"], self.name)

        last_done_set = False
        #has he solved all tasks? --> set LastDone
        if count_successful == num_tasks:
            data = {'user_id': str(userid), 'now': str(int(time.time()))}
            sql_cmd = ("UPDATE Users SET LastDone = datetime(:now, "
                       "'unixepoch', 'localtime') WHERE UserId == :user_id")
            curs.execute(sql_cmd, data)
            cons.commit()
            last_done_set = True

        cons.close()

        return last_done_set

####
# check_and_set_first_successful
####
    def check_and_set_first_successful(self, user_id, task_nr):
        """
        Set FirstSuccessful field of a UserTask, if not set, to last submission
        """

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], \
                                     self.name)

        # check if allready previous successful submission, if not set it
        data = {'user_id': user_id, 'task_nr': task_nr}
        sql_cmd = ("SELECT FirstSuccessful FROM UserTasks "
                   "WHERE UserId = :user_id AND TaskNr = :task_nr")
        curs.execute(sql_cmd, data)
        res = curs.fetchone()
        if res[0] is None:
            # get last submission number
            sql_cmd = ("SELECT NrSubmissions FROM UserTasks "
                       "WHERE UserId = :user_id AND TaskNr = :task_nr")
            curs.execute(sql_cmd, data)
            res = curs.fetchone()
            submission_nr = int(res[0])
            # set first successful
            data['subnr'] = submission_nr
            sql_cmd = ("UPDATE UserTasks SET FirstSuccessful = :subnr "
                       "WHERE UserId = :user_id AND TaskNr = :task_nr")
            curs.execute(sql_cmd, data)
            cons.commit()

            #update statistics only on FirstSuccessful
            self.increment_db_taskcounter('NrSuccessful', \
                                           str(task_nr))
            self.increment_db_taskcounter('NrSubmissions', \
                                           str(task_nr))

            # insert into SucessfulTasks, if it is already existent ignore
            data = {'user_id': user_id, 'task_nr': task_nr}

            sql_cmd = ("INSERT OR IGNORE INTO SuccessfulTasks (UserId, TaskNr) "
                       "VALUES (:user_id, :task_nr)")
            curs.execute(sql_cmd, data)
            cons.commit()

        cons.close()

####
# read_specialmessage
#
####
    def read_specialmessage(self, msgname):
        """
        read a special message from the DB
        """

        curc, conc = c.connect_to_db(self.dbs["course"], \
                                     self.queues["logger"], \
                                     self.name)

        data = {'msgname': msgname}
        sql_cmd = ("SELECT EventText FROM SpecialMessages "
                   "WHERE EventName = :msgname")
        curc.execute(sql_cmd, data)
        res = curc.fetchone()
        conc.close()

        if not res:
            logmsg = ("Error reading the Specialmessage named {0} from the "
                      "database").format(msgname)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

            message = "Hi something went wrong. Please contact the course admin"
        else:
            message = str(res[0])

        return message

####
# generate_status_update
####
    def generate_status_update(self, user_id, user_email, cur_task):
        """
        generate the e-mail body for response to a status mail
        """

        curc, conc = c.connect_to_db(self.dbs["course"], \
                                     self.queues["logger"], \
                                     self.name)
        curs, cons = c.connect_to_db(self.dbs["semester"], \
                                     self.queues["logger"], \
                                     self.name)

        #get user name
        data = {'user_id': user_id}
        sql_cmd = "SELECT Name FROM Users WHERE UserId = :user_id"
        curs.execute(sql_cmd, data)
        user_name = curs.fetchone()[0]

        #get the done tasks
        data = {'user_id': user_id}
        sql_cmd = ("SELECT TaskNr FROM SuccessfulTasks WHERE UserId = :user_id")
        curs.execute(sql_cmd, data)
        rows_nrs = curs.fetchall()

        if not rows_nrs:
            successfulls = None
        else:
            nrs = []
            for row_nrs in rows_nrs:
                nrs.append(str(row_nrs[0]))
            successfulls = ','.join(nrs)


        #get current user score
        if successfulls != None:
            sql_cmd = ("SELECT SUM(Score) FROM TaskConfiguration "
                       "WHERE TaskNr IN ({0})").format(successfulls)
            curc.execute(sql_cmd)
            cur_score = curc.fetchone()[0]
        else:
            cur_score = 0

        conc.close()
        cons.close()

        msg = ("Hi,\n\nYou requested your status, here you go:\n\n"
               "Username: {0}\nEmail: {1}\nCurrent Task: {2}\nSuccessfully "
               "finished TaskNrs: {3}\nYour current Score: {4}\n") \
               .format(str(user_name), user_email, str(cur_task), successfulls, str(cur_score))

        #Last done?
        if self.has_last_done(user_id):
            msg = msg + "\nYou solved all the tasks for this course for now.\n"

        # Commented because we need to find a better way for when skipping
        # Is activated, for now we assume the students get the deadline somwhere
        # else
        #try:
        #    cur_deadline = c.get_task_deadline(self.dbs["course"], cur_task, \
        #                                       self.queues["logger"], self.name)
        #    cur_start = c.get_task_starttime(self.dbs["course"], cur_task, \
        #                                     self.queues["logger"], self.name)

        #    msg = "{0}\nStarttime current Task: {1}\n".format(msg, cur_start)
        #    msg = "{0}Deadline current Task: {1}".format(msg, cur_deadline)
        #except:
        #    msg = "{0}\nNo more deadlines for you -- all Tasks are finished!".format(msg)

        msg = msg + "\n\nSo long, and thanks for all the fish!"

        return msg

####
# generate_tasks_list
####
    def generate_tasks_list(self):
        """
        Generate the email body for response to list tasks.
        """

        curc, conc = c.connect_to_db(self.dbs["course"], \
                                     self.queues["logger"], \
                                     self.name)

        msg = ("Hi,\n\nYou requested the list of tasks for the "
               "course, here you go:\n\n")

        sql_cmd = ("SELECT TaskNr, TaskName, TaskStart, TaskDeadline, Score "
                   "FROM TaskConfiguration")

        curc.execute(sql_cmd)
        rows = curc.fetchall()

        for row in rows:
            msg = msg + ("Task Number: {0}\nTask Name: {1}\nStart: {2}\n"
                         "Deadline: {3}\nScore: {4}\n") \
                       .format(row[0], row[1], row[2], row[3], row[4])
            msg = msg + 40*"-" + "\n\n"

        msg += "\n\nSo long, and thanks for all the fish!"

        conc.close()

        return msg

####
# archive_message
####
    def archive_message(self, message_id, is_finished_job=False):
        """
        trigger archivation of an e-mail
        """

        logmsg = "request archiving of message with message_id {0}".format(message_id)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        c.archive_message(self.queues['archive'], message_id, is_finished_job)

####
# send_out_email
####
    def send_out_email(self, recipient, message, msg_type, retry_cnt):
        """
        connect to the smtp server and send out an e-mail
        """

        try:
            logmsg=""

            # DEBUG: Just a debug excpetion for testing failed email sending
            #if msg_type == "Status":
            #    raise Exception("Fake Exception for testing resending")

            # connecting to smtp server
            if self.smtp_info["security"] == 'ssl':
                server = smtplib.SMTP_SSL(self.smtp_info["server"], int(self.smtp_info["port"]))
            else:
                server = smtplib.SMTP(self.smtp_info["server"], int(self.smtp_info["port"]))

            #server.ehlo_or_helo_if_needed()
            server.ehlo()

            if self.smtp_info["security"] == 'starttls':
                server.starttls()

            server.login(self.smtp_info["user"], self.smtp_info["passwd"])
        except smtplib.SMTPConnectError:
            logmsg = "Error while login to server with security= " + \
                     self.smtp_info["security"] + " , port= " + str(self.smtp_info["port"])
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
        except smtplib.SMTPAuthenticationError:
            logmsg = ("Authentication error")
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
        except Exception as exc:
            logmsg = str(exc)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            logmsg = "Error with server connection with security= " + \
                     self.smtp_info["security"] + " , port= " + str(self.smtp_info["port"])
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
        finally:
            if logmsg != "":
                # failed to send the mail, retry according to config
                self.resend_mail(msg_type,recipient,message,retry_cnt)

                try:
                     server.close()
                except Exception as exc:
                    logmsg = str(exc)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                return

        try:
            # DEBUG: Just a debug exception for testing failed email sending
            #if msg_type == "NoMultipleRequest":
            #    raise Exception("Fake Exception for testing resending")
            #if msg_type == "RetrySendingFailedMail":
            #    if retry_cnt<9:
            #        raise Exception("Fake Exception for testing resending")

            server.sendmail(self.smtp_info["mail"], recipient.split(','), message)

            c.log_a_msg(self.queues["logger"], self.name,\
            "Successfully sent an e-mail of type '{0}' to {1}!".format(msg_type, recipient), "INFO")
            c.increment_db_statcounter(self.dbs["semester"], 'nr_mails_sent', \
                                       self.queues["logger"], self.name)
        except Exception as exc:
            logmsg = str(exc)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            c.log_a_msg(self.queues["logger"], self.name, ("Failed to send out an e-mail of type "
                        "'{0} for user {1}'!").format(msg_type,recipient), "ERROR")

            # failed to send the mail, retry according to config
            self.resend_mail(msg_type, recipient, message,retry_cnt)
            try:
                server.close()
            except Exception as exc:
                logmsg = str(exc)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
            return

        try:
            server.close()
        except Exception as exc:
            logmsg = str(exc)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")



####
# handle resending a failed mail
####
    def resend_mail(self, msg_type, recipient, message,retry_cnt):

        if msg_type == "RetrySendingFailedMail":
            if retry_cnt < self.smtp_info["mail_retries"]:
                retry_cnt =retry_cnt+1
                time.sleep(5)
                c.log_a_msg(self.queues["logger"], self.name, ("Retrying to send out of type '{0} "
                            "for user {1}' for {2} time!").format(msg_type,recipient,retry_cnt), "INFO")
                self.queues["sender"].put(dict({"recipient": recipient, "user_id": "",
                    "message_type": "RetrySendingFailedMail", "task_nr": "", "body": message,
                    "message_id": "", "retry_cnt": retry_cnt}))
            else:
                c.log_a_msg(self.queues["logger"], self.name, ("Could not resend email of type '{0} "
                    "for user {1}'. Reached maximum retry number!").format(msg_type,recipient), "ERROR")

        else:
            c.log_a_msg(self.queues["logger"], self.name, ("Retrying to send out of type '{0} for "
                " user {1}'!").format(msg_type,recipient), "INFO")
            self.queues["sender"].put(dict({"recipient": recipient, "user_id": "",
                "message_type": "RetrySendingFailedMail", "task_nr": "", "body": message,
                "message_id": "", "retry_cnt": 0}))
        return

####
# read_text_file
####
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
            c.log_a_msg(self.queues["logger"], self.name, \
                        "Failed to read from config file", "WARNING")

        return message_text

####
# assemble_email
####
    def assemble_email(self, msg, message_text, attachments):
        """
        assemble e-mail content
        """

        msg.attach(MIMEText(message_text, 'plain', 'utf-8'))

        # If the message is a task description, we might want to
        # add some attachments.  These ar given as a list by the
        # attachments parameter
        logmsg = "List of attachements: {0}".format(attachments)
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        if str(attachments) != 'None':
            for next_attachment in attachments:
                try:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(open(next_attachment, "rb").read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(next_attachment)))
                    msg.attach(part)
                except:
                    logmsg = "Failed to add an attachement: {0}".format(next_attachment)
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

        # The following message my be helpful during debugging - but
        # if you use attachments, your log-file will grow very fast
        # therefore it was commented out.
        # logmsg = "Prepared message: \n" + str(msg)
        # c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
        return msg

####
# handle_next_mail()
####
    def handle_next_mail(self):
        """
        parse the subject/content of a mail and take appropriate action.
        """

        #blocking wait on sender_queue
        next_send_msg = self.queues["sender"].get(True)

        task_nr = str(next_send_msg.get('task_nr'))
        message_id = str(next_send_msg.get('message_id'))
        user_id = str(next_send_msg.get('user_id'))
        recipient = str(next_send_msg.get('recipient'))
        message_type = str(next_send_msg.get('message_type'))

        if message_type == "RetrySendingFailedMail":
            retry_cnt = int(next_send_msg.get('retry_cnt'))

        curs, cons = c.connect_to_db(self.dbs["semester"], self.queues["logger"], \
                                     self.name)
        curc, conc = c.connect_to_db(self.dbs["course"], self.queues["logger"], \
                                     self.name)

        attachments = []

        # prepare fields for the e-mail
        msg = MIMEMultipart()
        msg['From'] = self.smtp_info["mail"]
        msg['To'] = recipient
        logmsg = "RECIPIENT: " + recipient
        c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

        msg['Date'] = formatdate(localtime=True)

        if message_type == "Task":
        #################
        #       TASK    #
        #################
            logmsg = "Task in send_queue: " + str(next_send_msg)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            # 2 Cases:
            # allow_requests == "once" or "multiple" -> send Task anyway
            # allow_requests == "no" : check if he is at a higher task_nr,
            #                          if yes: do not send

            cur_task = c.user_get_current_task(self.dbs["semester"], user_id, \
                                               self.queues["logger"], self.name)
            at_higher_task = (cur_task > int(task_nr))

            should_not_send = (self.allow_requests == "no") and at_higher_task

            if should_not_send:
                logmsg = ("Task sending initiated, but user already reveived "
                          "this task!!!")
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                return

            data = {'task_nr': str(task_nr)}
            sql_cmd = ("SELECT TaskName FROM TaskConfiguration "
                       "WHERE TaskNr == :task_nr")

            curc.execute(sql_cmd, data)
            res = curc.fetchone()

            if not res:
                logmsg = ("Failed to fetch Configuration for TaskNr: "
                          "{0} from the database! Table "
                          "TaskConfiguration corrupted?").format(task_nr)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")

                message_text = ("Sorry, but something went wrong... "
                                "probably misconfiguration or missing"
                                "configuration of Task {0}").format(task_nr)
                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(recipient, msg.as_string(), \
                                    message_type, 0)
                self.archive_message(message_id)

                return

            task_name = res[0]
            description_path = self.course_info['tasks_dir'] + \
                               '/' + task_name + '/description.txt'

            if not os.path.isfile(description_path):
                logmsg = "No description.txt found for Task {0}.".format(task_nr)
                c.log_a_msg(self.queues["logger"], self.name, \
                        logmsg, "ERROR")

                message_text = ("Sorry, but something went wrong... "
                                "probably misconfiguration or missing"
                                "configuration of Task {0}").format(task_nr)
                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(recipient, msg.as_string(), message_type, 0)
                self.archive_message(message_id)
                return

            msg['Subject'] = "Description Task" + str(task_nr)
            task_deadline = c.get_task_deadline(self.dbs["course"], task_nr,
                                                self.queues["logger"], self.name)
            dl_text = "\nDeadline for this Task: {0}\n".format(task_deadline)

            message_text = self.read_text_file(description_path) \
                               + dl_text

            data = {'task_nr': str(task_nr), 'user_id': user_id}
            sql_cmd = ("SELECT TaskAttachments FROM UserTasks "
                       "WHERE TaskNr == :task_nr AND UserId == :user_id")
            curs.execute(sql_cmd, data)
            res = curs.fetchone()

            logmsg = "got the following attachments: " + str(res)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, \
                        "DEBUG")
            if res:
                attachments = str(res[0]).split()
            else:
                attachments = ""

            msg = self.assemble_email(msg, message_text, attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

            # Everything went okay -> adjust cur_task_nr
            c.user_set_current_task(self.dbs["semester"], task_nr, user_id, \
                                    self.queues["logger"], self.name)

        elif message_type == "Failed":
        #################
        #    FAILED     #
        #################
            # did user already solve this task?
            data = {"user_id":user_id, "task_nr":task_nr}
            sql_cmd = ("SELECT UserId FROM UserTasks WHERE UserId = :user_id "
                       "AND TaskNr = :task_nr AND FirstSuccessful IS NOT NULL")
            curs.execute(sql_cmd, data)
            res = curs.fetchone()
            task_already_solved = (res != None)

            #only update stat if user did not solve this task
            if not task_already_solved:
                self.increment_db_taskcounter('NrSubmissions', task_nr)

            path_to_msg = "users/{0}/Task{1}".format(user_id, task_nr)
            error_msg = self.read_text_file("{0}/error_msg".format(path_to_msg))
            msg['Subject'] = "Failure Task" + task_nr
            message_text = "Error report:\n\n""" + error_msg

            reply_attachments = []

            try:
                logmsg = "searching attachments in: {0}/error_attachments".format(path_to_msg)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                ats = os.listdir("{0}/error_attachments".format(path_to_msg))
                logmsg = "got the following attachments: {0}".format(ats)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                for next_attachment in ats:
                    reply_attachments.append("{0}/error_attachments/{1}".format(path_to_msg, next_attachment))
            except:
                logmsg = "no attachments for failed task."
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            msg = self.assemble_email(msg, message_text, reply_attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, 0)

            # archive and notify that worker finished
            self.archive_message(message_id, is_finished_job=True)

        elif message_type == "Success":
        #################
        #    SUCCESS    #
        #################
            msg['Subject'] = "Success Task " + task_nr
            message_text = "You solved the task successfully. Congratulations!"
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)

            #set first done if not set yet
            self.check_and_set_first_successful(user_id, task_nr)

            # last done had to be set now? --> Send Congrats
            if self.check_and_set_last_done(user_id):
                #new message, prepare it
                msg = MIMEMultipart()
                msg['From'] = self.smtp_info["mail"]
                msg['To'] = recipient
                logmsg = "RECIPIENT: " + recipient
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                msg['Date'] = formatdate(localtime=True)

                message_text = self.read_specialmessage('CONGRATS')
                msg['Subject'] = "Congratulations on solving all Tasks!"
                msg = self.assemble_email(msg, message_text, '')
                self.send_out_email(recipient, msg.as_string(), "LastSolved", 0)

            # archive and notify that worker finished
            self.archive_message(message_id, is_finished_job=True)

        elif message_type == "PluginResult":
        ######################
        #    PLUGINRESULT    #
        ######################
            path_to_msg = "users/{0}/Task{1}".format(user_id, task_nr)
            plugin_msg_file = "{0}/plugin_msg.json".format(path_to_msg)
            plugin_error = False
            is_success = False

            # Does the json file exist?
            if not os.path.isfile(plugin_msg_file):
                logmsg = ("Found no json file while assembling plugin result "
                    "message for Task {0} and User {1}!").format(task_nr, user_id)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                plugin_error = True

            # json file exists
            else:
                # try open and read json file
                try:
                    with open(plugin_msg_file) as f:
                        plugin_msg_data = json.loads(f.read())
                        if "Subject" not in plugin_msg_data or \
                           "Message" not in plugin_msg_data or \
                           "IsSuccess" not in plugin_msg_data:
                            raise Exception("Message, Subject or IsSuccess not defined!")

                        msg['Subject'] = plugin_msg_data['Subject']
                        message_text = plugin_msg_data['Message']
                        is_success = plugin_msg_data['IsSuccess']

                except Exception as error:
                    logmsg = ("Error reading plugin result json file for "
                        "Task {0} and User {1}: {2}!")\
                        .format(task_nr, user_id, str(error))
                    c.log_a_msg(self.queues["logger"], self.name, logmsg, "ERROR")
                    plugin_error = True

            # handle errors and alert to admins
            if plugin_error:
                msg['Subject'] = "Plugin Error Task" + task_nr
                message_text = ("There is no feedback from the plugin. "
                    "Please contact the course admin")

                c.send_email(self.queues["sender"], "", user_id, \
                             "TaskAlert", task_nr, "", message_id)

            # collect error_attachments
            reply_attachments = []

            try:
                logmsg = "searching attachments in: {0}/error_attachments"\
                    .format(path_to_msg)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                ats = os.listdir("{0}/error_attachments".format(path_to_msg))
                logmsg = "got the following attachments: {0}".format(ats)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                for next_attachment in ats:
                    reply_attachments.append("{0}/error_attachments/{1}"\
                        .format(path_to_msg, next_attachment))
            except:
                logmsg = "no attachments for task."
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")

            # send out email
            msg = self.assemble_email(msg, message_text, reply_attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, 0)

            # archive and notify that worker finished
            self.archive_message(message_id, is_finished_job=True)

            # set first successfull, TODO: this is based on simulation for now
            self.check_and_set_first_successful(user_id, task_nr)

        elif message_type == "SecAlert":
        #################
        #  SEC ALERT    #
        #################

            # get error log
            path_to_msg = "users/{0}/Task{1}".format(user_id, task_nr)
            error_msg = self.read_text_file("{0}/error_msg".format(path_to_msg))
           
            # send security alert to admins
            admin_mails = ",".join(self.get_admin_emails())
            msg['To'] = admin_mails
            message_text = ("Security Alert: User {}, Task {}:\n\n""").format(user_id,task_nr) 
            message_text = message_text+ error_msg
            msg['Subject'] = "Security Alert User: " + recipient
            msg = self.assemble_email(msg, message_text, '')

            self.send_out_email(admin_mails, msg.as_string(), message_type, 0)
        
        elif message_type == "TaskAlert":
        #################
        #   TASK ALERT  #
        #################
            admin_mails = ",".join(self.get_admin_emails())

            msg['To'] = admin_mails
            msg['Subject'] = "Task Error Alert Task{0} User{1}".format( \
                             str(task_nr), str(user_id))
            message_text = ("There was an error with the Task {0} " \
                            "and User {1}. Check the logfiles(tasks.stderr, tasks.stdout, "
                            "autosub.log) to find what caused it.").format(task_nr, user_id)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(admin_mails, msg.as_string(), message_type, 0)

        elif message_type == "TaskErrorNotice":
        ####################
        # TASKERROR NOTICE #
        ####################
            admins = ",".join(self.get_admin_emails())
            msg['Subject'] = "Error processing your last message"
            message_text = ("There was an error processing your last message, please write an "
                            "email to the administrators {0} and tell them about the time and what you did last. "
                            "They will work on resolving the issue as soon as possible.").format(admins)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)

            # archive, is_finished_job=True for tester errors, so the job can be
            # deleted from the active jobs
            # in the case this error is from a generator, the is_finished will be
            # ignored as the message_id will not be in the active jobs (see
            # fetcher.py)
            self.archive_message(message_id, is_finished_job=True)

        elif message_type == "Status":
        #################
        #    STATUS     #
        #################
            msg['Subject'] = "Your current status"
            message_text = self.generate_status_update(user_id, recipient, \
                                                       task_nr)
            numtasks = c.get_num_tasks(self.dbs["course"], self.queues["logger"], \
                                       self.name)

            if int(numtasks) >= int(task_nr):
                #also attach current task
                data = {'task_nr': str(task_nr), 'user_id': user_id}
                sql_cmd = ("SELECT TaskAttachments FROM UserTasks "
                           "WHERE TaskNr == :task_nr AND UserId == :user_id")
                curs.execute(sql_cmd, data)
                res = curs.fetchone()
                logmsg = "got the following attachments: " + str(res)
                c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
                if res:
                    attachments = str(res[0]).split()
                msg = self.assemble_email(msg, message_text, attachments)
                self.send_out_email(recipient, msg.as_string(), message_type, 0)
                self.archive_message(message_id)
            else:
                msg = self.assemble_email(msg, message_text, attachments)
                self.send_out_email(recipient, msg.as_string(), message_type, 0)
                self.archive_message(message_id)

        elif message_type == "TasksList":
        #################
        #   TASKSLIST   #
        #################
            msg['Subject'] = "List of tasks"
            message_text = self.generate_tasks_list()
            msg = self.assemble_email(msg, message_text, attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "InvalidTask":
        #################
        # INVALID TASK  #
        #################
            msg['Subject'] = "Invalid Task Number"
            message_text = self.read_specialmessage('INVALID')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "TaskNotSubmittable":
        #########################
        # TASK NOT SUBMITTABLE  #
        #########################
            msg['Subject'] = "Submission for Task{0} not possible".format(str(task_nr))
            message_text = self.read_specialmessage('TASKNOTSUBMITTABLE')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "TaskNotActive":
        #########################
        #    TASK NOT ACTIVE    #
        #########################
            msg['Subject'] = "Task{0} not active yet".format(str(task_nr))
            message_text = self.read_specialmessage('TASKNOTACTIVE')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "NoMultipleRequest":
        #########################
        #  NO MULTIPLE REQUEST  #
        #########################
	    # also attach task variant (e.g. if user lost it)
            data = {'task_nr': str(task_nr), 'user_id': user_id}
            sql_cmd = ("SELECT TaskAttachments FROM UserTasks "
                       "WHERE TaskNr == :task_nr AND UserId == :user_id")
            curs.execute(sql_cmd, data)
            res = curs.fetchone()
            logmsg = "got the following attachments: " + str(res)
            c.log_a_msg(self.queues["logger"], self.name, logmsg, "DEBUG")
            if res:
                attachments = str(res[0]).split()

            # assemble mail
            msg['Subject'] = "Already received Task{0}".format(str(task_nr))
            message_text = self.read_specialmessage('NOMULTIPLEREQUEST')
            msg = self.assemble_email(msg, message_text, attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "CurLast":
        #################
        #   CUR LAST    #
        #################
            # we still need to increment the users task counter!
            c.user_set_current_task(self.dbs["semester"], task_nr, user_id, \
                                   self.queues["logger"], self.name)
            msg['Subject'] = "Task{0} is not available yet".format(str(task_nr))
            message_text = self.read_specialmessage('CURLAST')
            message_text = "{0}\n\nThe Task is currently scheduled for: {1}".format(message_text, \
                   c.get_task_starttime(self.dbs["course"], str(task_nr), \
                   self.queues["logger"], self.name))
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "DeadTask":
        #################
        #   DEAD TASK   #
        #################
            msg['Subject'] = "Deadline for Task{0} has passed.".format(str(task_nr))
            message_text = self.read_specialmessage('DEADTASK')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "Usage":
        #################
        #     USAGE     #
        #################
            msg['Subject'] = "Usage"
            message_text = self.read_specialmessage('USAGE')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "Question":
        #################
        #   QUESTION    #
        #################
            msg['Subject'] = "Question received"
            message_text = self.read_specialmessage('QUESTION')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)

        elif message_type == "QFwd":
        #################
        #      QFWD     #
        #################
            orig_mail = next_send_msg.get('body')
            orig_from = orig_mail['from']

            orig_mail.replace_header("From", self.smtp_info["mail"])
            orig_mail.replace_header("To", recipient)

            if task_nr:
                orig_mail.replace_header("Subject", "Question Task" + task_nr +" from " + orig_from)
            else:
                orig_mail.replace_header("Subject", "Question from " + orig_from)

            self.send_out_email(recipient, orig_mail.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "Welcome":
        #################
        #    WELCOME    #
        #################
            msg['Subject'] = "Welcome!"
            message_text = self.read_specialmessage('WELCOME')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "RegOver":
        #################
        #    REGOVER    #
        #################
            msg['Subject'] = "Registration Deadline has passed"
            message_text = self.read_specialmessage('REGOVER')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "NotAllowed":
        #################
        #  NOT ALLOWED  #
        #################
            msg['Subject'] = "Registration not successful."
            message_text = self.read_specialmessage('NOTALLOWED')
            message_text = message_text.replace("[[recipient]]",recipient)
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "DeletedFromWhitelist":
        ############################
        #  DELETED FROM WHITELIST  #
        ############################
            msg['Subject'] = "Not whitelisted anymore"
            message_text = self.read_specialmessage('DeletedFromWhitelist')
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

        elif message_type == "RetrySendingFailedMail":
        #################################
        #  RETRY SENDING A FAILED MAIL  #
        #################################
            orig_mail = next_send_msg.get('body')
            self.send_out_email(recipient, orig_mail, message_type,retry_cnt)
        else:
        #################
        #   UNKNOWN    #
        #################
            c.log_a_msg(self.queues["logger"], self.name, \
                        "Unkown Message Type in the sender_queue!", "ERROR")
            msg = self.assemble_email(msg, message_text, '')
            self.send_out_email(recipient, msg.as_string(), message_type, 0)
            self.archive_message(message_id)

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
        c.log_a_msg(self.queues["logger"], self.name, \
                    "Starting Mail Sender Thread!", "INFO")

        while True:
            self.handle_next_mail()
