import sqlite3 as lite
import optparse

####
#  connect_to_db()
####
def connect_to_db(dbname):
   # connect to sqlite database ...
   try:
      con = lite.connect(dbname)
   except:
      print ("Failed to connect to database: %s", dbname)

   cur = con.cursor()
   return cur, con


### main :-) ################

parser = optparse.OptionParser()
parser.add_option("-u", "--userid", dest="userid", type="int",
           help=("UserID of the user."))
parser.set_defaults(userid=0)
parser.add_option("-t", "--tasknr", dest="tasknr", type="int",
           help=("TaskNr this operation concerns."))
parser.set_defaults(tasknr=0)
parser.add_option("-p", "--parameters", dest="generation_parameters", type="string",
           help=("Parameters used to generate this example."))
parser.set_defaults(generation_parameters="")
parser.add_option("-a", "--attachments", dest="attachments", type="string",
           help=("Space seperated list of attachments."))
parser.set_defaults(attachments="")

opts, args = parser.parse_args()

if (opts.userid == 0) or (opts.tasknr == 0):
   print ("Make sure to pass a UserID (-u) AND a TaskNr (-t)!")

cur, con = connect_to_db('../semester.db')

sql_cmd = "SELECT * FROM UserTasks WHERE TaskNr==" + str(opts.tasknr) + " AND UserId ==" + str(opts.userid) +";"
cur.execute(sql_cmd);

res = cur.fetchall()

if not res:
   sql_cmd="INSERT INTO UserTasks (TaskNr, UserId, TaskParameters, TaskDescription, TaskAttachments, NrSubmissions, FirstSuccessful) \
                            VALUES(:TaskNr , :UserId, :TaskParameters , :TaskDescriptions, :TaskAttachments, :NrSubmissions, :FirstSuccessful)"
   data={'TaskNr': opts.tasknr ,
         'UserId': opts.userid,
         'TaskParameters': opts.generation_parameters, 
         'TaskDescriptions': None,
         'TaskAttachments':opts.attachments,
         'NrSubmissions':0,
         'FirstSuccessful': None}
   
   cur.execute(sql_cmd,data);
   con.commit();
else:
   print ("entry already exists!")

con.close()
