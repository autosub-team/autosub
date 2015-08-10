########################################################################
# fetcher.py -- fetch e-mails from the mailbox
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import email, imaplib, os, time
import sqlite3 as lite
import re #regex
import datetime
import common as c

class mailFetcher (threading.Thread):
   def __init__(self, threadID, name, job_queue, sender_queue, gen_queue, autosub_user, autosub_passwd, autosub_imapserver, logger_queue, poll_period):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.job_queue = job_queue
      self.sender_queue = sender_queue
      self.gen_queue = gen_queue
      self.autosub_user = autosub_user
      self.autosub_pwd = autosub_passwd
      self.imapserver = autosub_imapserver
      self.logger_queue = logger_queue
      self.poll_period = poll_period

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
   # If a new user registers, add_new_user() is used to add the necessary entries
   # to the database
   ####
   def add_new_user(self, user_name, user_email, cur, con):
      logmsg = 'New Account: User: %s' % user_name 
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      sql_cmd="INSERT INTO Users (UserId, Name, Email, FirstMail, LastDone, CurrentTask) VALUES(NULL, '" + user_name + "', '" + user_email + "'," + "datetime("+str(int(time.time()))+", 'unixepoch', 'localtime')" + ", NULL, 1);"
      cur.execute(sql_cmd);
      con.commit();

      # the new user has now been added to the database. Next we need
      # to send him an email with the first task.

      # read back the new users UserId and create a directory for putting his
      # submissions in:
      sql_cmd="SELECT UserId FROM Users WHERE Email='" + user_email +"';"
      cur.execute(sql_cmd);
      res = cur.fetchone();
      userid = str(res[0])
      dirname = 'users/'+ userid
      c.check_dir_mkdir(dirname, self.logger_queue, self.name)

      # NOTE: messageid is empty, cause this will be sent out by the welcome message!
      curc, conc = c.connect_to_db('course.db', self.logger_queue, self.name)
      sql_cmd="SELECT GeneratorExecutable FROM TaskConfiguration WHERE TaskNr == 1"
      curc.execute(sql_cmd);
      res = curc.fetchone();
      conc.close() 
    
      if res != None:
         logmsg="Calling Generator Script: " + str(res[0])
         c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
         logmsg="UserID " + userid + ",UserEmail " + user_email 
         c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
         self.gen_queue.put(dict({"UserId": userid, "UserEmail": user_email, "TaskNr": "1", "MessageId": ""}))
      else:
         # If there is no generator script, we assume, that there is a static description.txt
         # which shall be used.
         c.send_email(self.sender_queue, user_email, userid, "Task", "1", "", "")


   ####
   # take_new_result()
   #
   # A new result for task TaskNr has been submitted -- store in the users directory
   # structure.
   ####
   def take_new_results(self, user_email, TaskNr, cur, con, mail, messageid):
      # read back the new users UserId and create a directory for putting his
      # submissions in:
      sql_cmd="SELECT UserId FROM Users WHERE Email='" + user_email +"';"
      cur.execute(sql_cmd);
      user_id = cur.fetchone();

      detach_dir = 'users/'+str(user_id[0])+"/Task"+str(TaskNr)
      ts = datetime.datetime.now()
      current_dir = detach_dir + "/Task"+str(TaskNr)+"_" + str(ts.year) + str(ts.month) + str(ts.day) + "_" + str(ts.hour) + "_" + str(ts.minute) + "_" +  str(ts.second) + "_" +  str(ts.microsecond) 
      c.check_dir_mkdir(current_dir, self.logger_queue, self.name)


      # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
      for part in mail.walk():
      # multipart are just containers, so we skip them
         if part.get_content_maintype() == 'multipart':
            continue

         # is this part an attachment ?
         if part.get('Content-Disposition') is None:
            continue

         filename = part.get_filename()
         counter = 1

         # if there is no filename, we create one with a counter to avoid duplicates
         if not filename:
            filename = 'part-%03d%s' % (counter, 'bin')
            counter += 1

         att_path = os.path.join(current_dir, filename)

         #Check if its already there
         if not os.path.isfile(att_path) :
            # finally write the stuff
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()

      cmd = "rm " + detach_dir + "/*" + " 2> /dev/null"
      os.system(cmd)

      cmd = "cp -R " +  current_dir + "/* " + detach_dir + " > /dev/null"
      os.system(cmd)

      # Next, let's handle the task that shall be checked, and send a job
      # request to the job_queue. The workers can then get it from there.
      self.job_queue.put(dict({"UserId": user_id[0], "UserEmail": user_email,"message_type": "Task", "taskNr": TaskNr, "MessageId": messageid}))

   ####
   # a_question_was_asked()
   #
   # Process a question that was asked by a student
   ###
   def a_question_was_asked(self, cur, con, user_email, mail, messageid):
      logmsg = 'The user has a question, please take care of that!'
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      c.send_email(self.sender_queue, user_email, "", "Question", "", "", "")
      admin_mail = self.get_admin_email()
      c.send_email(self.sender_queue, admin_mail, "", "QFwd", "", mail, messageid)

      self.increment_db_statcounter(cur, con, 'nr_questions_received')

   def a_status_is_requested(self, cur, con, user_email, messageid):
      sqlcmd = "SELECT UserId,CurrentTask FROM Users WHERE Email=='"+user_email+"';"
      cur.execute(sqlcmd);
      res = cur.fetchone();

      UserId=res[0]
      CurrentTask=res[1]
      c.send_email(self.sender_queue, user_email, UserId, "Status", CurrentTask, "", "")
      self.increment_db_statcounter(cur, con, 'nr_status_requests')

   ####
   # connect_to_imapserver()
   ####
   def connect_to_imapserver(self):
      try:
         # connecting to the gmail imap server
         m = imaplib.IMAP4_SSL(self.imapserver)
         m.login(self.autosub_user,self.autosub_pwd)
      except imaplib.IMAP4.abort:
         logmsg = "Login to server was aborted (probably a server-side problem). Trying to connect again ..."
         c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
         #m.close()
         return 0
      except imaplib.IMAP4.error:
         logmsg = "Got an error when trying to connect to the imap server. Trying to connect again ..."
         c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
         return 0
      except:
         logmsg = "Got an unknown exception when trying to connect to the imap server. Trying to connect again ..."
         c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
         return 0

      logmsg = "Successfully logged into imap server"
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
      return m

   ####
   # fetch new (unseen) e-mails from the Inbox 
   ####
   def fetch_new_emails(self, m):
      try:
         m.select("Inbox") # here you a can choose a mail box like INBOX instead
         # use m.list() to get all the mailboxes
      except:
         logmsg = "Failed to select inbox"
         c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

      resp, items = m.search(None, "UNSEEN") # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
      return items[0].split() # getting the mails id

   ####
   #  check_if_whitelisted(user_email)
   #
   #  check if the given e-mail address is in the whitelist
   ####
   def check_if_whitelisted(self, cur, con, user_email):
      sqlcmd = "SELECT * FROM WhiteList WHERE Email == '"+ user_email + "';"
      cur.execute(sqlcmd);
      res = cur.fetchone();
      if res != None:
         return 1
      else:
         logmsg = "Got Mail from a User not on the WhiteList: " + user_email
         c.log_a_msg(self.logger_queue, self.name, logmsg, "Warning");
         self.increment_db_statcounter(cur, con, 'nr_non_registered')
         return 0

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
   # loop_code()
   #
   # The code run in the while True loop of the mail fetcher thread.
   ####
   def loop_code(self):
      cur,con = c.connect_to_db('semester.db', self.logger_queue, self.name)

      m = self.connect_to_imapserver()

      if m != 0:
         items = self.fetch_new_emails(m)

         # iterate over all new e-mails and take action according to the structure of the subject line
         for emailid in items:

            self.increment_db_statcounter(cur, con, 'nr_mails_fetched')

            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc

            mail = email.message_from_bytes(data[0][1]) # parsing the mail content to get a mail object

            mail_subject = str(mail['subject'])
            from_header = str(mail['From'])
            split_header = str(from_header).split("<")
            user_name = split_header[0]
            try:
               user_email = str(split_header[1].split(">")[0])
            except:
               user_email = str(mail['From'])

            messageid = mail.get('Message-ID')

            whitelisted = self.check_if_whitelisted(cur, con, user_email)

            if whitelisted:
 
               sql_cmd="SELECT UserId FROM Users WHERE Email='" + str(user_email) +"';"
               cur.execute(sql_cmd);
               res = cur.fetchall();
               if res:
                  logmsg = "Got mail from an already known user!"
                  c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")

                  if re.search('[Rr][Ee][Ss][Uu][Ll][Tt]', mail_subject):
                     searchObj = re.search( '[0-9]+', mail_subject, )
                     if (int(searchObj.group()) <= self.get_num_Tasks()):
                        logmsg = 'Processing a Result'
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                        self.take_new_results(user_email, searchObj.group(), cur, con, mail, messageid)
                     else:
                        logmsg = 'Given Task number is higher than actual Number of Tasks!'
                        c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                        c.send_email(self.sender_queue, user_email, "", "InvalidTask", "", "", messageid)
                  elif re.search('[Qq][Uu][Ee][Ss][Tt][Ii][Oo][Nn]', mail_subject):
                     self.a_question_was_asked(cur, con, user_email, mail, messageid)
                  elif re.search('[Ss][Tt][Aa][Tt][Uu][Ss]', mail_subject):
                     self.a_status_is_requested(cur, con, user_email, messageid)
                  else:
                     logmsg = 'Got a kind of message I do not understand. Sending a usage mail...' 
                     c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")
                     c.send_email(self.sender_queue, user_email, "", "Usage", "", "", messageid)

               else:
                  self.add_new_user(user_name, user_email, cur, con)
                  c.send_email(self.sender_queue, user_email, "", "Welcome", "", "", messageid)

            else:
                  c.send_email(self.sender_queue, user_email, "", "NotAllowed", "", "", messageid)

         try:
            m.close()
         except imaplib.IMAP4.abort:
            logmsg = "Closing connection to server was aborted (probably a server-side problem). Trying to connect again ..."
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
            #m.close()
         except imaplib.IMAP4.error:
            logmsg = "Got an error when trying to connect to the imap server. Trying to connect again ..."
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
         except:
            logmsg = "Got an unknown exception when trying to connect to the imap server. Trying to connect again ..."
            c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")
         finally:   
            logmsg = "closed connection to imapserver"
            c.log_a_msg(self.logger_queue, self.name, logmsg, "INFO")
   
      con.close() # close connection to sqlite db, so others can use it as well.
      time.sleep(self.poll_period) # it's enough to check e-mails every minute

   ####
   # thread code for the fetcher thread.
   ####
   def run(self):
      c.log_a_msg(self.logger_queue, self.name, "Starting Mail Fetcher Thread!", "INFO")

      logmsg = "Imapserver: '" + self.imapserver + "'"
      c.log_a_msg(self.logger_queue, self.name, logmsg, "DEBUG")

      # This thread is running as a daemon thread, this is the while(1) loop that is running until
      # the thread is stopped by the main thread
      while True:
         self.loop_code()


      logmsg = "Exiting fetcher - this should NEVER happen!"
      c.log_a_msg(self.logger_queue, self.name, logmsg, "ERROR")

