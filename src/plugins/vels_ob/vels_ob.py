#!/usr/bin/env python3

import optparse
import json
import sys
import os
import swagger_client as api_vels_ob
from swagger_client.rest import ApiException

################
# PARSE PARAMS #
################
parser = optparse.OptionParser()

parser.add_option("--user_task_dir", dest="user_task_dir", type="string")
parser.add_option("--task_dir", dest="task_dir", type="string")
parser.add_option("--user_id", dest="user_id", type="int")
parser.add_option("--task_nr", dest="task_nr", type="int")
parser.add_option("--password", dest="password", type="string")
parser.add_option("--server", dest="server", type="string")
parser.add_option("--port", dest="port", type="string")

(options, args) = parser.parse_args()

#TODO: check if all params passed

user_task_dir = options.user_task_dir
task_dir = options.task_dir
user_id  = options.user_id
task_nr = options.task_nr
password = options.password
server = options.server
port = options.port

############
# REST API #
############
api_con = api_vels_ob.Configuration()
api_con.host = "{}:{}/api".format(server, port)
task_instance = api_vels_ob.TaskApi(api_vels_ob.ApiClient(api_con))

#################
# READ IN FILES #
#################
task_plugin_dir = os.path.join(task_dir, "plugin_data/vels_ob")
ent_file = os.path.join(task_plugin_dir, "entity.vhdl")
settings_file = os.path.join(task_plugin_dir, "settings.json")

with open(ent_file) as f:
    entity_ob = f.read()

with open(settings_file) as f:
    settings = json.loads(f.read())

beh_file = os.path.join(user_task_dir,settings["beh_file"])
with open(beh_file) as f:
    beh = f.read().splitlines(True)

#######################
# ADJUST THE BEH FILE #
#######################
index_to_insert = None
for index in range(0,len(beh)):
    if "architecture behavior" in beh[index]:
        index_to_insert = index
        break

if not index_to_insert:
    sys.stderr.write("Could not find architecture line")
    sys.exit(1)

for alias in settings["aliases"]:
    beh.insert(index_to_insert+1,alias+"\n")

#######################
# ASSEMBLE FINAL FILE #
#######################
final_file_name = os.path.join(user_task_dir, "vels_ob_{}.vhd".format(user_id))

with open(final_file_name, "w") as f:
    f.write(entity_ob)
    f.write("".join(beh))

############################
# SEND TO VELS_OB WITH API #
############################
try:
    result = task_instance.create_a_new_task(str(user_id), final_file_name)
    print("Rest API returned " + str(result))

except ApiException as e:
    sys.stderr.write("Error with REST API")
    sys.stderr.write(str(e))
    sys.exit(1)

###############
# RETURN JSON #
###############
json_data = {
     "Subject" : "Synthesis Result for Task{}".format(str(task_nr)),
     "Message" : server +":" + str(port) + "/"+str(user_id),
     "IsSuccess" : True \
}
file_name = os.path.join(user_task_dir, "plugin_msg.json")

with open(file_name, "w") as f:
    json.dump(json_data, f)

sys.exit(0)
