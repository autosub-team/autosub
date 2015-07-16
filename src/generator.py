import threading
import sqlite3 as lite
import datetime

class taskGenerator (threading.Thread):
   def __init__(self, threadID, name, gen_queue, sender_queue, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.gen_queue = gen_queue
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue

   ####
   # log_a_msg()
   ####
   def log_a_msg(self, msg, loglevel):
      self.logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": self.name}))

   def run(self):
      self.log_a_msg("Task Generator thread started", "INFO")

