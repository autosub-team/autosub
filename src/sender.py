########################################################################
# sender.py -- send out e-mails based on the info given by fetcher.py
#       or worker.py
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
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

class mailSender (threading.Thread):
   def __init__(self, threadID, name, sender_queue, autosub_mail, autosub_passwd, autosub_smtpserver, logger_queue, numTasks):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.sender_queue = sender_queue
      self.gmail_user = autosub_mail
      self.gmail_pwd = autosub_passwd
      self.smtpserver = autosub_smtpserver
      self.logger_queue = logger_queue
      self.numTasks = numTasks

   ####
   # log_a_msg()
   ####
   def log_a_msg(self, msg, loglevel):
         self.logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": self.name}))

   ####
   # increment_db_statcounter()
   ####
   def increment_db_statcounter(self, cur, con, countername):
      sql_cmd = "UPDATE StatCounters SET value=(SELECT value FROM StatCounters WHERE Name=='" + countername + "')+1 WHERE Name=='" + countername + "';"
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
   # user_set_current_task()
   ####
   def user_set_current_task(self, cur, con, tasknr, userid):
      sql_cmd = "UPDATE Users SET current_task='" + str(tasknr) + "' where UserId=='" + str(userid) + "';"
      cur.execute(sql_cmd)
      con.commit();


   ####
   #
   ####
   def check_and_set_last_done(self, cur, con, userid):
      sql_cmd = "SELECT last_done FROM users WHERE UserId==" + userid + ";"
      cur.execute(sql_cmd)
      res = cur.fetchone();
      logmsg = "RES: "+ str(res[0])
      self.log_a_msg(logmsg, "DEBUG")

      if str(res[0]) == "None":
         sql_cmd = "UPDATE users SET last_done=" + str(int(time.time())) + " where UserId==" + userid + ";"
         cur.execute(sql_cmd)
         con.commit();


   def backup_message(self, messageid):
      logmsg= "backup not implemented yet; messageid: " + messageid
      self.log_a_msg(logmsg, "DEBUG")

   def run(self):
      self.log_a_msg("Starting Mail Sender Thread!", "INFO")

      while True:
         next_send_msg = self.sender_queue.get(True) #blocking wait on sender_queue

         con = lite.connect('autosub.db')
         cur = con.cursor()

         attachments = ''

         # prepare fields for the e-mail
         msg = MIMEMultipart()
         msg['From'] = self.gmail_user
         msg['To'] = str(next_send_msg.get('recipient'))
         logmsg= "RECIPIENT: " + str(next_send_msg.get('recipient'))
         self.log_a_msg(logmsg, "DEBUG")
         
         msg['Date'] = formatdate(localtime = True)

         TaskNr = str(next_send_msg.get('Task'))
         messageid = str(next_send_msg.get('MessageId'))

         has_text = 0;

         if (str(next_send_msg.get('message_type')) == "Task"):
            if (self.numTasks+1 == int(TaskNr)): # last task solved!
               msg['Subject'] = "Congratulations!" 
               path_to_msg = "congratulations.txt"
               has_text = 1;

               self.user_set_current_task(cur, con, TaskNr, str(next_send_msg.get('UserId')))
               self.check_and_set_last_done(cur, con, next_send_msg.get('UserId'))

            else: # at least one more task to do: send out the description
               msg['Subject'] = "Description Task" + TaskNr 
               path_to_msg = "tasks/task" + TaskNr + "/description.txt"
               has_text = 1;
               path_to_attachments = "tasks/task" + TaskNr + "/attachments"
               if os.path.exists(path_to_attachments):
                  attachments = os.listdir(path_to_attachments)

               self.user_set_current_task(cur, con, TaskNr, str(next_send_msg.get('UserId')))

            # we are sending out the description for TaskNr, but we want to
            # update the stats for TaskNr-1 !
            self.increment_db_taskcounter(cur, con, 'nr_submissions', str(int(TaskNr)-1))
            self.increment_db_taskcounter(cur, con, 'nr_successful', str(int(TaskNr)-1))

            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "Failed"):
            self.increment_db_taskcounter(cur, con, 'nr_submissions', TaskNr)
            UserId = str(next_send_msg.get('UserId'))
            path_to_msg = "users/"+ UserId + "/Task" + TaskNr + "/error_msg"
            fp = open(path_to_msg, 'r')
            error_msg = fp.read()
            fp.close()
            msg['Subject'] = "Task" + TaskNr + ": submission rejected"
            TEXT = "Error report:\n\n""" + error_msg
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "SecAlert"):
            msg['To'] = "andi.platschek@gmail.com"
            path_to_msg = "users/"+ next_send_msg.get('UserId') + "/Task" + TaskNr + "/error_msg"
            fp = open(path_to_msg, 'r')
            error_msg = fp.read()
            fp.close()
            msg['Subject'] = "Autosub Security Alert User:" + str(next_send_msg.get('recipient'))
            TEXT = "Error report:\n\n""" + error_msg
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "Success"):
            msg['Subject'] = "Task " + TaskNr + " submitted successfully"
            TEXT = "Congratulations!"
            # no backup of message -- this is done after the new task
            # description was sent to the user!
         elif (str(next_send_msg.get('message_type')) == "InvalidTask"):
            msg['Subject'] = "Invalid Task Number"
            path_to_msg = "invalidtask.txt"
            has_text = 1;
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "Usage"):
            msg['Subject'] = "Autosub Usage"
            path_to_msg = "usage.txt"
            has_text = 1;
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "Question"):
            msg['Subject'] = "Question received"
            path_to_msg = "question.txt"
            has_text = 1;
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "QFwd"):
            orig_mail = next_send_msg.get('Body')
            msg['Subject'] = "Question from " + orig_mail['from']
            TEXT = "Original subject: " + orig_mail['subject'] + "\n\n" + orig_mail.get_payload()
            self.backup_message(messageid)
         elif (str(next_send_msg.get('message_type')) == "Welcome"):
            msg['Subject'] = "Welcome!"
            path_to_msg = "welcome.txt"
            has_text = 1;
            self.backup_message(messageid)
         else:
            self.log_a_msg("Unkown Message Type in the sender_queue!","ERROR")
            self.backup_message(messageid)

         # Read Text for E-Mail Body from a config file
         if has_text:
            fp = open(path_to_msg, 'r')
            TEXT = fp.read()
            fp.close()

         msg.attach( MIMEText(TEXT, 'plain', 'utf-8') )

         # If the message is a task description, we might want to
         # add some attachments. those are assumed to be located in
         # directory called attachments, the list of the files
         # in that directory was retrieved earlier.
         for f in attachments:
            part = MIMEBase('application', "octet-stream")
            full_f = path_to_attachments + "/" + f
            part.set_payload( open(full_f,"rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
            msg.attach(part)

         logmsg = "Prepared message: \n" + str(msg)
         self.log_a_msg(logmsg, "DEBUG")
 
         try:
            server = smtplib.SMTP(self.smtpserver, 587) # port 465 doesn't seem to work!
            server.ehlo()
            server.starttls()
            server.login(self.gmail_user, self.gmail_pwd)
            server.sendmail(self.gmail_user, str(next_send_msg.get('recipient')), msg.as_string())
            server.close()
            self.log_a_msg("Successfully sent an e-mail!", "DEBUG")
            self.increment_db_statcounter(cur, con, 'nr_mails_sent')
         except:
            self.log_a_msg("Failed to send out an e-mail!", "ERROR")

         con.close()
