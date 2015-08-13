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
   def __init__(self, threadID, name, sender_queue, autosub_mail, autosub_user, autosub_passwd, autosub_smtpserver, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.sender_queue = sender_queue
      self.autosub_user = autosub_user
      self.mail_user = autosub_mail
      self.mail_pwd = autosub_passwd
      self.smtpserver = autosub_smtpserver
      self.logger_queue = logger_queue

   ####
   # get_admin_email()
   ####
   def get_admin_email(self):
      curc, conc = c.connect_to_db('course.db', self.logger_queue, self.name)
      sqlcmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'admin_email'"
      curc.execute(sqlcmd)
      adminEmail = str(curc.fetchone()[0])
      conc.close()

      return adminEmail

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
   # user_set_currentTask()
   #
   # Set the currentTask of the user with userid to tasknr.
   ####
   def user_set_currentTask(self, cur, con, tasknr, userid):
      sql_cmd = "UPDATE Users SET CurrentTask='" + str(tasknr) + "' where UserId=='" + str(userid) + "';"
      cur.execute(sql_cmd)
      con.commit();

   ####
   # user_get_currentTask()
   #
   # Get the surrentTask of the user with userid.
   ####
   def user_get_currentTask(self, cur, con, userid):
      sql_cmd = "Select CurrentTask from Users where UserId=='" + str(userid) + "';"
      cur.execute(sql_cmd)
      res = cur.fetchone();
      return str(res[0]);



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
   #
   ####
   def read_specialmessage(self, msgname):
      curc, conc = c.connect_to_db('course.db', self.logger_queue, self.name)
      sqlcmd = "SELECT EventText FROM SpecialMessages WHERE EventName=='" + msgname + "';"
      curc.execute(sqlcmd)
      res = curc.fetchone();
      conc.close()
      return str(res[0])

   ####
   # get_numTasks()
   ####
   def get_num_Tasks(self):
      curc, conc = c.connect_to_db('course.db', self.logger_queue, self.name)
      sqlcmd = "SELECT Content FROM GeneralConfig WHERE ConfigItem == 'num_tasks'"
      curc.execute(sqlcmd)
      numTasks = int(curc.fetchone()[0])
      conc.close()

      return numTasks

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

      conc = lite.connect('course.db')
      curc = conc.cursor()
      sqlcmd = "SELECT sum(Score) FROM TaskConfiguration WHERE TaskNr <" + str(curtask[0])
      curc.execute(sqlcmd)
      curscore = curc.fetchone()
      curc.close()

      if str(curscore[0]) == 'None': # no task solved yet.
         tmpscore = 0
      else:
         tmpscore = curscore[0]

      return "Username: " + str(uname[0]) + "\nEmail: " + user_email + "\nCurrent Task: " + str(curtask[0]) + "\n Your current Score: " + str(tmpscore) # + "\nRestration Date: " + str(rdate[0]) + "\nRegistration Time: " + str(rtime[0])

   ####
   # backup_message()
   #
   # Just a stub, in the future, the message with the messageid shall be moved
   # into an archive folder on the mailserver.
   ####
   def backup_message(self, messageid):
      logmsg= "backup not implemented yet; messageid: " + messageid
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

   def send_out_email(self, recipient, message, cur, con):
      try:
         server = smtplib.SMTP(self.smtpserver, 587) # port 465 doesn't seem to work!
         server.ehlo()
         server.starttls()
         server.login(self.autosub_user, self.mail_pwd)
         server.sendmail(self.mail_user, recipient, message)
         server.close()
         c.log_a_msg(self.logger_queue, self.name, "Successfully sent an e-mail!", "DEBUG")
         self.increment_db_statcounter(cur, con, 'nr_mails_sent')
      except:
         c.log_a_msg(self.logger_queue, self.name, "Failed to send out an e-mail!", "ERROR")

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
      # add some attachments. those are assumed to be located in
      # directory called attachments, the list of the files
      # in that directory was retrieved earlier.
      if str(attachments) != 'None':
         for f in attachments:
            part = MIMEBase('application', "octet-stream")
            part.set_payload(open(f,"rb").read() )
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
            msg.attach(part)

      logmsg = "Prepared message: \n" + str(msg)
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
      return msg

   def handle_next_mail(self):
      next_send_msg = self.sender_queue.get(True) #blocking wait on sender_queue

      cur, con = c.connect_to_db('semester.db', self.logger_queue, self.name)

      attachments = ''

      # prepare fields for the e-mail
      msg = MIMEMultipart()
      msg['From'] = self.mail_user
      msg['To'] = str(next_send_msg.get('recipient'))
      logmsg= "RECIPIENT: " + str(next_send_msg.get('recipient'))
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
         
      msg['Date'] = formatdate(localtime = True)

      TaskNr = str(next_send_msg.get('Task'))
      messageid = str(next_send_msg.get('MessageId'))

      if (str(next_send_msg.get('message_type')) == "Task"):
         numTasks = self.get_num_Tasks()
         ctasknr=self.user_get_currentTask(cur, con, str(next_send_msg.get('UserId')))
         if (numTasks+1 == int(TaskNr)): # last task solved!
            msg['Subject'] = "Congratulations!" 
            TEXT = self.read_specialmessage('CONGRATS')

            if ((int(TaskNr)-1) == (int(ctasknr))):
               #statistics shall only be udated on the first successful submission
               self.user_set_currentTask(cur, con, TaskNr, str(next_send_msg.get('UserId')))
               self.increment_db_taskcounter(cur, con, 'NrSuccessful', str(int(TaskNr)-1))
               self.increment_db_taskcounter(cur, con, 'NrSubmissions', str(int(TaskNr)-1))
               self.check_and_set_lastDone(cur, con, next_send_msg.get('UserId'))

            msg = self.assemble_email(msg, TEXT, '')
            self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
         else: # at least one more task to do: send out the description
            # only send the task description, after the first successful submission
            if ((int(TaskNr)-1) == (int(ctasknr)) or int(ctasknr) == 1):
               msg['Subject'] = "Description Task" + str(TaskNr) 

               curcCourse, concCourse = c.connect_to_db('course.db', self.logger_queue, self.name)
               sql_cmd="SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == "+str(TaskNr)
               curcCourse.execute(sql_cmd)
               paths = curcCourse.fetchone()
               if not paths:
                  c.log_a_msg(self.logger_queue, self.name, "It seems, the Path to Task "+ str(TaskNr) + " is not configured.", "WARNING")
                  TEXT = "Sorry, but something went wrong... probably misconfiguration or missing configuration of Task " + str(TaskNr)
                  msg = self.assemble_email(msg, TEXT, '')
                  self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
               else:
                  path_to_task = str(paths[0])
                  concCourse.close() 

                  path_to_msg = path_to_task + "/description.txt"
                  TEXT = self.read_text_file(path_to_msg)
                  logmsg="used sql comand: SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + TaskNr + " AND UserId == '"+ str(next_send_msg.get('UserId')) + "';"
                  c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG");

                  sql_cmd="SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + TaskNr + " AND UserId == '"+ str(next_send_msg.get('UserId')) + "';"
                  cur.execute(sql_cmd)
                  res = cur.fetchone()

                  logmsg = "got the following attachments: " + str(res)
                  c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                  if res:
                     attachments = str(res[0]).split()

                  #statistics shall only be udated on the firs succesful submission
                  self.user_set_currentTask(cur, con, TaskNr, str(next_send_msg.get('UserId')))
                  self.increment_db_taskcounter(cur, con, 'NrSuccessful', str(int(TaskNr)-1))
                  self.increment_db_taskcounter(cur, con, 'NrSubmissions', str(int(TaskNr)-1))

                  msg = self.assemble_email(msg, TEXT, attachments)
                  self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)


         self.backup_message(messageid)

      elif (str(next_send_msg.get('message_type')) == "Failed"):
         self.increment_db_taskcounter(cur, con, 'NrSubmissions', TaskNr)
         UserId = str(next_send_msg.get('UserId'))
         path_to_msg = "users/"+ UserId + "/Task" + TaskNr + "/error_msg"
         error_msg = self.read_text_file(path_to_msg)
         msg['Subject'] = "Task" + TaskNr + ": submission rejected"
         TEXT = "Error report:\n\n""" + error_msg
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
         self.backup_message(messageid)

      elif (str(next_send_msg.get('message_type')) == "SecAlert"):
         admin_mail = self.get_admin_email()
         msg['To'] = admin_mail
         path_to_msg = "users/"+ next_send_msg.get('UserId') + "/Task" + TaskNr + "/error_msg"
         error_msg = self.read_text_file(path_to_msg)
         msg['Subject'] = "Autosub Security Alert User:" + str(next_send_msg.get('recipient'))
         TEXT = "Error report:\n\n""" + error_msg
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
         self.backup_message(messageid)

      elif (str(next_send_msg.get('message_type')) == "Success"):
         msg['Subject'] = "Task " + TaskNr + " submitted successfully"
         TEXT = "Congratulations!"
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
         # no backup of message -- this is done after the new task
         # description was sent to the user!
      elif (str(next_send_msg.get('message_type')) == "Status"):
         msg['Subject'] = "Your Current Status"
         TEXT = self.generate_status_update(cur, con, str(next_send_msg.get('recipient')))
         numTasks = self.get_num_Tasks()
         if (int(numTasks) >=  int(TaskNr)):
            #also attach current task
            sql_cmd="SELECT TaskAttachments FROM UserTasks WHERE TaskNr == " + str(TaskNr) + " AND UserId == '"+ str(next_send_msg.get('UserId')) + "';"
            cur.execute(sql_cmd)
            res = cur.fetchone()
            logmsg = "got the following attachments: " + str(res)
            c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
            if res:
               attachments = str(res[0]).split()
            msg = self.assemble_email(msg, TEXT, attachments)
            self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "InvalidTask"):
         msg['Subject'] = "Invalid Task Number"
         TEXT = self.read_specialmessage('INVALID')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "Usage"):
         msg['Subject'] = "Autosub Usage"
         TEXT = self.read_specialmessage('USAGE')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "Question"):
         msg['Subject'] = "Question received"
         TEXT = self.read_specialmessage('QUESTION')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "QFwd"):
         orig_mail = next_send_msg.get('Body')
         msg['Subject'] = "Question from " + orig_mail['from']
         TEXT = "Original subject: " + orig_mail['subject'] + "\n\n" + orig_mail.get_payload()
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "Welcome"):
         msg['Subject'] = "Welcome!"
         TEXT = self.read_specialmessage('WELCOME')
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      elif (str(next_send_msg.get('message_type')) == "NotAllowed"):
         msg['Subject'] = "Registration Not Successful."
         TEXT = self.read_specialmessage('NOTALLOWED')
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)
      else:
         c.log_a_msg(self.logger_queue, self.name, "Unkown Message Type in the sender_queue!","ERROR")
         self.backup_message(messageid)
         msg = self.assemble_email(msg, TEXT, '')
         self.send_out_email(str(next_send_msg.get('recipient')), msg.as_string(), cur, con)

      con.close()


   ####
   # thread code of the sender thread.
   ####
   def run(self):
      c.log_a_msg(self.logger_queue, self.name, "Starting Mail Sender Thread!", "INFO")

      while True:
         self.handle_next_mail()


