########################################################################
# fetcher.py -- fetch e-mails from the mailbox
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import email, imaplib, os, time
import sqlite3 as lite
import re #regex
import datetime

class mailFetcher (threading.Thread):
   def __init__(self, threadID, name, job_queue, sender_queue, autosub_mail, autosub_passwd, autosub_imapserver, logger_queue, numTasks):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.job_queue = job_queue
      self.sender_queue = sender_queue
      self.gmail_user = autosub_mail
      self.gmail_pwd = autosub_passwd
      self.imapserver = autosub_imapserver
      self.logger_queue = logger_queue
      self.admin_mail = "andi.platschek@gmail.com"
      self.numTasks = numTasks

   ####
   # Check if all databases, tables, etc. are available, or if they have to be created.
   # if non-existent --> create them
   ####
   def init_ressources(self):
      # connect to sqlite database ...
      con = lite.connect('autosub.db')
      # ... and check whether the Users table exists. If not: create it
      cur = con.cursor()
      cur.execute("SELECT name FROM sqlite_master WHERE type == 'table' AND name = 'Users';")
      res = cur.fetchall()
      if res:
         logmsg = 'table Users exists'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
      else:
         logmsg = 'table Users does not exist'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
         con.execute("CREATE TABLE Users(UserId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, email TEXT, first_mail INT, last_done INT, current_task INT)")

      # ... do the same for the Task_Stats table
      cur.execute("SELECT name FROM sqlite_master WHERE type == 'table' AND name = 'TaskStats';")
      res = cur.fetchall()
      if res:
         logmsg = 'table TaskStats exists'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
         #TODO: in this case, we might want to check if one entry per task is already there, and add new
         #      empty entries in case a task does not have one. This is only a problem, if the number of
         #      tasks in the config file is changed AFTER the TaskStats table has been changed!
      else:
         logmsg = 'table TaskStats does not exist'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
         con.execute("CREATE TABLE TaskStats(TaskId INTEGER PRIMARY KEY, nr_submissions INT, nr_successful INT)")
         for t in range (1, self.numTasks+1):
            sql_cmd="INSERT INTO TaskStats (TaskId, nr_submissions, nr_successful) VALUES("+ str(t) + ", 0, 0);"
            cur.execute(sql_cmd);
         con.commit();

      # ... do the same for the StatCounters table
      cur.execute("SELECT name FROM sqlite_master WHERE type == 'table' AND name = 'StatCounters';")
      res = cur.fetchall()
      if res:
         logmsg = 'table StatCounters exists'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
      else:
         logmsg = 'table StatCounters does not exist'
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
         con.execute("CREATE TABLE StatCounters(CounterId INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, value INT)")
         # add the stat counter entries and initialize them to 0:
         sql_cmd="INSERT INTO StatCounters (CounterId, Name, value) VALUES(NULL, 'nr_mails_fetched', 0);"
         cur.execute(sql_cmd);
         sql_cmd="INSERT INTO StatCounters (CounterId, Name, value) VALUES(NULL, 'nr_mails_sent', 0);"
         cur.execute(sql_cmd);
         sql_cmd="INSERT INTO StatCounters (CounterId, Name, value) VALUES(NULL, 'nr_questions_received', 0);"
         cur.execute(sql_cmd);
         con.commit();
 
      if not os.path.exists("users"):
         os.mkdir("users")
         logmsg = "Created directory users!"
         self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
      else:
         logmsg = "Directory users already exists!"
         self.logger_queue.put(dict({"msg": logmsg, "type": "WARNING", "loggername": self.name}))

      con.close() # close here, since we re-open the databse in the while(True) loop

   ####
   # If a new user registers, add_new_user() is used to add the necessary entries
   # to the database
   ####
   def add_new_user(self, user_name, user_email, cur, con):
      self.logger_queue.put(dict({"msg": "Got mail from a new user - creating a new account:", "type": "DEBUG", "loggername": self.name}))
      logmsg= 'New User: %s' % user_name 
      self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))

      sql_cmd="INSERT INTO Users (UserId, Name, email, first_mail, last_done, current_task) VALUES(NULL, '" + user_name + "', '" + user_email + "', '" + str(int(time.time())) + "', NULL, 1);"
      cur.execute(sql_cmd);
      con.commit();

      # the new user has now been added to the database. Next we need
      # to send him an email with the first task.
      # NOTE: messageid is empty, cause this will be sent out by the welcome message!
      self.sender_queue.put(dict({"recipient": user_email, "message_type": "Task", "Task": "1", "MessageId": ""}))

      # read back the new users UserId and create a directory for putting his
      # submissions in:
      sql_cmd="SELECT UserId FROM Users WHERE email='" + user_email +"';"
      cur.execute(sql_cmd);
      res = cur.fetchone();
      dirname = 'users/'+str(res[0])
      if not os.path.exists(dirname):
         os.mkdir(dirname)
      else:
         logmsg= "Warning: a directory for the new users ID already exists!"
         self.logger_queue.put(dict({"msg": logmsg, "type": "WARNING", "loggername": self.name}))

   ####
   # 
   ####
   def take_new_results(self, user_email, TaskNr, cur, con, mail, messageid):
      # read back the new users UserId and create a directory for putting his
      # submissions in:
      sql_cmd="SELECT UserId FROM Users WHERE email='" + user_email +"';"
      cur.execute(sql_cmd);
      user_id = cur.fetchone();
      detach_dir = 'users/'+str(user_id[0])+"/Task"+str(TaskNr)

      if not os.path.exists(detach_dir):
         os.mkdir(detach_dir)
           
      ts = datetime.datetime.now()
      current_dir = detach_dir + "/Task"+str(TaskNr)+"_" + str(ts.year) + str(ts.month) + str(ts.day) + "_" + str(ts.hour) + "_" + str(ts.minute) + "_" +  str(ts.second) + "_" +  str(ts.microsecond) 
      if not os.path.exists(current_dir):
         os.mkdir(current_dir)

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
   # Process a question that was asked by a student
   ###
   def a_question_was_asked(self, cur, con):
      logmsg = 'The user has a question, please manually take care of that!'
      self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))

      self.sender_queue.put(dict({"recipient": user_email, "UserId": "" ,"message_type": "Question", "Task": "", "MessageId": ""}))
      self.sender_queue.put(dict({"recipient": self.admin_mail, "UserId": "" ,"message_type": "QFwd", "Task": "", "Body": mail, "MessageId": messageid}))

      sql_cmd = "UPDATE StatCounters SET value=(SELECT value FROM StatCounters WHERE Name=='nr_questions_received')+1 WHERE Name=='nr_questions_received';"
      cur.execute(sql_cmd)
      con.commit();


   ####
   # The "main" routine of the fetcher thread.
   ####
   def run(self):
      self.logger_queue.put(dict({"msg": "Starting Mail Fetcher Thread!", "type": "INFO", "loggername": self.name}))

      self.init_ressources()

      # This thread is running as a daemon thread, this is the while(1) loop that is running until
      # the thread is stopped by the main thread
      while True:
         con = lite.connect('autosub.db')
         cur = con.cursor()
         try:
            # connecting to the gmail imap server
            m = imaplib.IMAP4_SSL(self.imapserver)
            m.login(self.gmail_user,self.gmail_pwd)
         except imaplib.IMAP4.abort:
            logmsg = "Login to server was aborted (probably a server-side problem). Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))
            #m.close()
         except imaplib.IMAP4.error:
            logmsg = "Got an error when trying to connect to the imap server. Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))
         except:
            logmsg = "Got an unknown exception when trying to connect to the imap server. Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))

         try:
            m.select("Inbox") # here you a can choose a mail box like INBOX instead
            # use m.list() to get all the mailboxes
         except:
            logmsg = "Failed to select inbox"
            self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))

         resp, items = m.search(None, "UNSEEN") # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
         items = items[0].split() # getting the mails id

         for emailid in items:

            sql_cmd = "UPDATE StatCounters SET value=(SELECT value FROM StatCounters WHERE Name=='nr_mails_fetched')+1 WHERE Name=='nr_mails_fetched';"
            cur.execute(sql_cmd)
            con.commit();

            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            mail = email.message_from_string(email_body) # parsing the mail content to get a mail object
            messageid = mail.get('Message-ID')
#            messageid = "42"
            logmsg="message-id: " + messageid
            self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))

            from_header = mail['from']
            split_header = from_header.split("<");
            user_name = split_header[0];
            try:
               user_email = split_header[1].split(">")[0];
            except:
               user_email = mail['from']
            mail_subject = mail['subject']

            sql_cmd="SELECT UserId FROM Users WHERE email='" + user_email +"';"
            cur.execute(sql_cmd);
            res = cur.fetchall();
            if res:
               logmsg = "Got mail from an already known user!"
               self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))

               if re.search('[Rr][Ee][Ss][Uu][Ll][Tt]', mail_subject):
                  searchObj = re.search( '[0-9]+', mail_subject, )
                  if (int(searchObj.group()) <= self.numTasks):
                     logmsg = 'Processing a Result'
                     self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
                     self.take_new_results(user_email, searchObj.group(), cur, con, mail, messageid)
                  else:
                     logmsg = 'Given Task number is higher than actual Number of Tasks!'
                     self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
                     self.sender_queue.put(dict({"recipient": user_email, "UserId": "" ,"message_type": "InvalidTask", "Task": "", "MessageId": messageid}))
               elif re.search('[Qq][Uu][Ee][Ss][Tt][Ii][Oo][Nn]', mail_subject):
                  self.a_question_was_asked(cur,con)
               else:
                  logmsg = 'Got a kind of message I do not understand. Sending a usage mail...' 
                  self.logger_queue.put(dict({"msg": logmsg, "type": "DEBUG", "loggername": self.name}))
                  self.sender_queue.put(dict({"recipient": user_email, "UserId": "" ,"message_type": "Usage", "Task": "", "MessageId": messageid}))

            else:
               self.add_new_user(user_name, user_email, cur, con)
               self.sender_queue.put(dict({"recipient": user_email, "UserId": "" ,"message_type": "Welcome", "Task": "", "MessageId": messageid}))

         try:
            m.close()
         except imaplib.IMAP4.abort:
            logmsg = "Closing connection to server was aborted (probably a server-side problem). Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))
            #m.close()
         except imaplib.IMAP4.error:
            logmsg = "Got an error when trying to connect to the imap server. Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))
         except:
            logmsg = "Got an unknown exception when trying to connect to the imap server. Trying to connect again ..."
            self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))
         finally:   
            logmsg = "closed connection to imapserver"
            self.logger_queue.put(dict({"msg": logmsg, "type": "INFO", "loggername": self.name}))
         
   
         con.close() # close connection to sqlite db, so others can use it as well.
         time.sleep(60) # it's enough to check e-mails every minute

      logmsg = "Exiting fetcher - this should NEVER happen!"
      self.logger_queue.put(dict({"msg": logmsg, "type": "ERROR", "loggername": self.name}))

