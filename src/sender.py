#######################################################################
# sender.py -- send out e-mails based on the info given by fetcher.py
#       or worker.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import smtplib, os, time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import sqlite3 as lite
import common as c

class mailSender (threading.Thread):
   def __init__(self, threadID, name, sender_queue, autosub_mail, autosub_user, autosub_passwd, autosub_smtpserver, logger_queue, arch_queue, coursedb, semesterdb):
      threading.Thread.__init__(self)
      self.threadID = threadID
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
      curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)
      sqlcmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'admin_email'"
      curc.execute(sqlcmd)
      result = str(curc.fetchone()[0])
      adminEmails = [email.strip() for email in result.split(',')] #split and put it in list
      conc.close()

      return adminEmails

   ####
   # increment_db_statcounter()
   ####
   def increment_db_statcounter(self, cur, con, countername):
      sql_cmd = "UPDATE StatCounters SET Value=(SELECT Value FROM StatCounters WHERE Name=='" + countername + "')+1 WHERE Name=='" + countername + "';"
      cur.execute(sql_cmd)
      con.commit();

   ####
   # increment_db_taskcounter()
   ####
   def increment_db_taskcounter(self, cur, con, countername, tasknr):
      sql_cmd = "UPDATE TaskStats SET " + countername + "=(SELECT "+ countername + " FROM TaskStats WHERE TaskId==" + tasknr + ")+1 WHERE TaskId==" + tasknr + ";"
      cur.execute(sql_cmd)
      con.commit();


   ####
   # check_and_set_lastDone()
   #
   # Check if the timestamp in lastDone has been set. If so, leave the old one
   # as we want to know when the user submitted the correct version of the last
   # task for the very first time.
   # If this is the first time, write the current timestamp into the database.
   ####
   def check_and_set_lastDone(self, cur, con, userid):
      sql_cmd = "SELECT LastDone FROM Users WHERE UserId==" + userid + ";"
      cur.execute(sql_cmd)
      res = cur.fetchone();
      logmsg = "RES: "+ str(res[0])
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      if str(res[0]) == 'None':
         sql_cmd = "UPDATE Users SET LastDone=" + "datetime("+str(int(time.time()))+", 'unixepoch', 'localtime')" + " where UserId==" + str(userid) + ";"
         cur.execute(sql_cmd)
         con.commit();
   
   ####
   # check_and_set_firstSuccessful
   #
   # set FirstSuccessful to last submission if not set yet
   ####
   def check_and_set_firstSuccessful(self,cur,con,UserId,TaskNr):

      # check if allready previous successful submission, if not set it
      sqlcmd="SELECT FirstSuccessful FROM UserTasks WHERE UserId = {0} AND TaskNr = {1};".format(UserId,TaskNr) 
      cur.execute(sqlcmd)
      res = cur.fetchone()
      if res[0] == None:
         # get last submission number
         sqlcmd="SELECT NrSubmissions FROM UserTasks WHERE UserId = {0} AND TaskNr = {1};".format(UserId,TaskNr)  
         cur.execute(sqlcmd)
         res = cur.fetchone()
         submissionNr=int(res[0])
         # set first successful
         sqlcmd="UPDATE UserTasks SET FirstSuccessful = {0} WHERE UserId = {1} AND TaskNr = {2};".format(submissionNr,UserId,TaskNr) 
         cur.execute(sqlcmd)
         con.commit()

   ####
   # read_specialmessage
   #
   ####
   def read_specialmessage(self, msgname):
      curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)
      sqlcmd = "SELECT EventText FROM SpecialMessages WHERE EventName=='" + msgname + "';"
      curc.execute(sqlcmd)
      res = curc.fetchone()
      conc.close()
      return str(res[0])

   ####
   # generate_status_update()
   ####
   def generate_status_update(self, cur, con, user_email):
      sqlcmd = "SELECT Name FROM Users WHERE Email=='" + user_email + "';"
      cur.execute(sqlcmd)
      uname = cur.fetchone()
      sqlcmd = "SELECT CurrentTask FROM Users WHERE Email=='" + user_email + "';"
      cur.execute(sqlcmd)
      curtask = cur.fetchone()

      conc = lite.connect(self.coursedb)
      curc = conc.cursor()
      sqlcmd = "SELECT sum(Score) FROM TaskConfiguration WHERE TaskNr <" + str(curtask[0])
      curc.execute(sqlcmd)
      curscore = curc.fetchone()
      curc.close()

      if str(curscore[0]) == 'None': # no task solved yet.
         tmpscore = 0
      else:
         tmpscore = curscore[0]

      msg =  "Username: {0}\nEmail: {1}\nCurrent Task: {2}\n Your current Score: {3}\n".format(str(uname[0]), user_email, str(curtask[0]), str(tmpscore))

      try:
         cur_deadline = c.get_task_deadline(str(curtask[0]), self.logger_queue, self.name)
         cur_start = c.get_task_starttime(str(curtask[0]), self.logger_queue, self.name)

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
      logmsg= "request backup of message with messageid: " + messageid
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      self.arch_queue.put(dict({"mid": messageid}))

   def send_out_email(self, recipient, message, msg_type, cur, con):
      try:
         server = smtplib.SMTP(self.smtpserver, 587) # port 465 doesn't seem to work!
         server.ehlo()
         server.starttls()
         server.login(self.autosub_user, self.mail_pwd)
         server.sendmail(self.mail_user, recipient, message)
         server.close()
         c.log_a_msg(self.logger_queue, self.name, "Successfully sent an e-mail of type '{0}'!".format(msg_type), "DEBUG")
         c.increment_db_statcounter(cur, con, 'nr_mails_sent')
      except:
         c.log_a_msg(self.logger_queue, self.name, "Failed to send out an e-mail of type '{0}'!".format(msg_type), "ERROR")

   def read_text_file(self, path_to_msg):
      try:
         fp = open(path_to_msg, 'r')
         TEXT = fp.read()
         fp.close()
      except:
         TEXT = "Even the static file was not available!"
         c.log_a_msg(self.logger_queue, self.name, "Failed to read from config file", "WARNING")

      return TEXT

   def assemble_email(self, msg, TEXT, attachments):
      msg.attach( MIMEText(TEXT, 'plain', 'utf-8') )

      # If the message is a task description, we might want to
      # add some attachments.  These ar given as a list by the
      # attachments parameter
      logmsg = "List of attachements: {0}".format(attachments)
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      if str(attachments) != 'None':
         for f in attachments:
            try:
               part = MIMEBase('application', "octet-stream")
               part.set_payload(open(f,"rb").read() )
               encoders.encode_base64(part)
               part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
               msg.attach(part)
            except:
               logmsg = "Faild to add an attachement: {0}".format(f)
               c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
               

      # The following message my be helpful during debugging - but if you use attachments, your log-file
      # will grow very fast -- therefore it was commented out.
#      logmsg = "Prepared message: \n" + str(msg)   
#      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
      return msg

   def handle_next_mail(self):
      #blocking wait on sender_queue
      next_send_msg = self.sender_queue.get(True) 
 
      TaskNr = str(next_send_msg.get('Task'))
      messageid = str(next_send_msg.get('MessageId'))
      UserId = str(next_send_msg.get('UserId'))
      recipient= str(next_send_msg.get('recipient'))
      message_type= str(next_send_msg.get('message_type'))

      cur, con = c.connect_to_db(self.semesterdb, self.logger_queue, self.name)
      curc, conc = c.connect_to_db(self.coursedb, self.logger_queue, self.name)
     
      attachments = []

      # prepare fields for the e-mail
      msg = MIMEMultipart()
      msg['From'] = self.mail_user
      msg['To'] = recipient
      logmsg= "RECIPIENT: " + recipient
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
         
      msg['Date'] = formatdate(localtime = True)

      if (message_type == "Task"):
         logmsg= "Task in send_queue: " + str(next_send_msg)
         c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
         numTasks = c.get_num_Tasks(self.coursedb, self.logger_queue, self.name)
         ctasknr = c.user_get_currentTask(cur, con, UserId)
         if (numTasks+1 == int(TaskNr)): # last task solved!
            msg['Subject'] = "Congratulations!" 
            TEXT = self.read_specialmessage('CONGRATS')

            if ((int(TaskNr)-1) == (int(ctasknr))):
               #statistics shall only be udated on the first successful submission
               c.user_set_currentTask(cur, con, TaskNr, UserId)
               self.increment_db_taskcounter(cur, con, 'NrSuccessful', str(int(TaskNr)-1))
               self.increment_db_taskcounter(cur, con, 'NrSubmissions', str(int(TaskNr)-1))
               self.check_and_set_lastDone(cur, con, UserId)

            msg = self.assemble_email(msg, TEXT, '')
            self.send_out_email(recipient, msg.as_string(),message_type, cur, con)
         else: # at least one more task to do: send out the description
            # only send the task description, after the first successful submission
            if ((int(TaskNr)-1) <= (int(ctasknr)) or int(ctasknr) == 1):
               msg['Subject'] = "Description Task" + str(TaskNr)

               dl_text = "\nDeadline for this Task: {0}\n".format(c.get_task_deadline(TaskNr, self.logger_queue, self.name))

               sql_cmd="SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == "+str(TaskNr)
               curc.execute(sql_cmd)
               paths = curc.fetchone()
               if not paths:
                  c.log_a_msg(self.logger_queue, self.name, "It seems, the Path to Task "+ str(TaskNr) + " is not configured.", "WARNING")
                  TEXT = "Sorry, but something went wrong... probably misconfiguration or missing configuration of Task " + str(TaskNr)
                  msg = self.assemble_email(msg, TEXT, '')
                  self.send_out_email(recipient, msg.as_string(),message_type, cur, con)
               else:
                  path_to_task = str(paths[0])
                  path_to_msg = path_to_task + "/description.txt"
                  TEXT = self.read_text_file(path_to_msg) + dl_text
                  logmsg="used sql comand: SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + TaskNr + " AND UserId == '"+ UserId + "';"
                  c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG");

                  sql_cmd="SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + TaskNr + " AND UserId == '"+ UserId + "';"
                  cur.execute(sql_cmd)
                  res = cur.fetchone()

                  logmsg = "got the following attachments: " + str(res)
                  c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                  if res:
                     attachments = str(res[0]).split()

                  #statistics shall only be udated on the firs succesful submission
                  c.user_set_currentTask(cur, con, TaskNr, UserId)
                  self.increment_db_taskcounter(cur, con, 'NrSuccessful', str(int(TaskNr)-1))
                  self.increment_db_taskcounter(cur, con, 'NrSubmissions', str(int(TaskNr)-1))

                  msg = self.assemble_email(msg, TEXT, attachments)
                  self.send_out_email(recipient, msg.as_string(),message_type, cur, con)


         self.backup_message(messageid)

      elif (message_type == "Failed"):
         self.increment_db_taskcounter(cur, con, 'NrSubmissions', TaskNr)
         path_to_msg = "users/{0}/Task{1}".format(UserId, TaskNr)
         error_msg = self.read_text_file("{0}/error_msg".format(path_to_msg))
         msg['Subject'] = "Task" + TaskNr + ": submission rejected"
         TEXT = "Error report:\n\n""" + error_msg

         reply_attachments = []

         try:
            logmsg = "searchin attachments in: {0}/error_attachments".format(path_to_msg)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            ats = os.listdir("{0}/error_attachments".format(path_to_msg))
            logmsg = "got the following attachments: {0}".format(ats)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            for a in ats:
                reply_attachments.append("{0}/error_attachments/{1}".format(path_to_msg, a))
         except:
            logmsg = "no attachments for failed task."
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

         msg = self.assemble_email(msg, TEXT, reply_attachments)
         self.send_out_email(recipient, msg.as_string(),message_type, cur, con)
         self.backup_message(messageid)

      elif (message_type == "SecAlert"):
         admin_mails = self.get_admin_emails()
         for admin_mail in admin_mails:
            msg['To'] = admin_mail
            path_to_msg = "users/"+ UserId + "/Task" + TaskNr + "/error_msg"
            error_msg = self.read_text_file(path_to_msg)
            msg['Subject'] = "Autosub Security Alert User:" + recipient
            TEXT = "Error report:\n\n""" + error_msg
            msg = self.assemble_email(msg, TEXT, '')
            self.send_out_email(admin_mail, msg.as_string(),message_type, cur, con)
            self.backup_message(messageid)

      elif (message_type == "TaskAlert"):
         admin_mails = self.get_admin_emails()
         for admin_mail in admin_mails:
            msg['To'] = admin_mail
            msg['Subject'] = "Autosub Task Error Alert Task " + TaskNr+ " User " + UserId
            TEXT = "Something went wrong with task/testbench analyzation for Task " + TaskNr +" and User " +UserId+ " . Either the entity or testbench analyzation threw an error."
            msg = self.assemble_email(msg, TEXT, '')
            self.send_out_email(admin_mail, msg.as_string(),message_type, cur, con)
            self.backup_message(messageid)

      elif (message_type == "Success"):
         msg['Subject'] = "Task " + TaskNr + " submitted successfully"
         TEXT = "Congratulations!"
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(),message_type, cur, con)
         #set first done if not set yet
         self.check_and_set_firstSuccessful(cur,con,UserId,TaskNr)
         
         # no backup of message -- this is done after the new task
         # description was sent to the user!
      elif (message_type == "Status"):
         msg['Subject'] = "Your Current Status"
         TEXT = self.generate_status_update(cur, con, recipient)
         numTasks = c.get_num_Tasks(self.coursedb, self.logger_queue, self.name)
         if (int(numTasks) >=  int(TaskNr)):
            #also attach current task
            sql_cmd="SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + str(TaskNr) + " AND UserId == '"+ UserId + "';"
            cur.execute(sql_cmd)
            res = cur.fetchone()
            logmsg = "got the following attachments: " + str(res)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            if res:
               attachments = str(res[0]).split()
            msg = self.assemble_email(msg, TEXT, attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
         else:
            msg = self.assemble_email(msg, TEXT, attachments)
            self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "InvalidTask"):
         msg['Subject'] = "Invalid Task Number"
         TEXT = self.read_specialmessage('INVALID')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "CurLast"):
         c.user_set_currentTask(cur, con, TaskNr, UserId) # we still need to increment the users task counter!
         msg['Subject'] = "Task{0} is not available yet".format(str(TaskNr))
         TEXT = self.read_specialmessage('CURLAST')
         TEXT = "{0}\n\nThe Task is currently scheduled for: {1}".format(TEXT, c.get_task_starttime(str(TaskNr), self.logger_queue, self.name))
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "DeadTask"):
         msg['Subject'] = "Deadline for Task{0} has passed.".format(str(TaskNr))
         TEXT = self.read_specialmessage('DEADTASK')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "Usage"):
         msg['Subject'] = "Autosub Usage"
         TEXT = self.read_specialmessage('USAGE')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "Question"):
         msg['Subject'] = "Question received"
         TEXT = self.read_specialmessage('QUESTION')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "QFwd"):
         orig_mail = next_send_msg.get('Body')
         msg['Subject'] = "Question from " + orig_mail['from']

         if orig_mail.get_content_maintype() == 'multipart':
            part = orig_mail.get_payload(0)
            mbody = part.get_payload()
            TEXT = "Original subject: " + orig_mail['subject'] + "\n\nNote: This e-mail contained attachments which have been removed!\n"
            TEXT = TEXT + "\n\nOriginal body:\n" + str(mbody) 
         else:
            mbody = orig_mail.get_payload()
            TEXT = "Original subject: " + orig_mail['subject'] + "\n\nOriginal body:\n" + str(mbody) 

         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "Welcome"):
         msg['Subject'] = "Welcome!"
         TEXT = self.read_specialmessage('WELCOME')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "RegOver"):
         msg['Subject'] = "Registration Deadline has passed"
         TEXT = self.read_specialmessage('REGOVER')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      elif (message_type == "NotAllowed"):
         msg['Subject'] = "Registration Not Successful."
         TEXT = self.read_specialmessage('NOTALLOWED')
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)
      else:
         c.log_a_msg(self.logger_queue, self.name, "Unkown Message Type in the sender_queue!","ERROR")
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(recipient, msg.as_string(), message_type, cur, con)

      con.close()
      conc.close() 


   ####
   # thread code of the sender thread.
   ####
   def run(self):
      c.log_a_msg(self.logger_queue, self.name, "Starting Mail Sender Thread!", "INFO")

      while True:
         self.handle_next_mail()
