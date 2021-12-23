import os
from datetime import datetime,timedelta

def __tail(filename, n=1, bs=1024):
    try:
        with open(filename) as f:
            f.seek(0,2)
            l = 1-f.read(1).count('\n')
            B = f.tell()
            while n >= l and B > 0:
                    block = min(bs, B)
                    B -= block
                    f.seek(B, 0)
                    l += f.read(block).count('\n')
            f.seek(B, 0)
            l = min(l,n)
            lines = f.readlines()[-l:]
            return lines
    except:
        return ["Error reading log at " + filename]

def __tail_error(filename, n=1, bs = 1024, key = "ERROR"):
    try:
        tail=(__tail(filename,n,bs))
        error_lines=[]
        for line in tail:
            if "ERROR" in line:
                error_lines.append(line)
        if(error_lines==[]):
            error_lines = ["No Errors found in the last {} log entries".format(n)]
        return error_lines
    except:
        return ["Error reading log at " + filename]

def __check_running(filename,polling_period = 30):
    try:
        tail=(__tail(filename,1))
        latest_timestamp = datetime.strptime(tail[0].split(",")[0],"%Y-%m-%d %H:%M:%S")
        delta_latest_timestamp = datetime.now()-latest_timestamp
        if(delta_latest_timestamp<timedelta(seconds=polling_period)):
            return True
        else:
            return False
    except:
        return False

@auth.requires_login()
def index():
    row=course(GeneralConfig.ConfigItem =='course_name').select(GeneralConfig.ALL).first()
    course_name = row.Content

    row=course(GeneralConfig.ConfigItem =='log_dir').select(GeneralConfig.ALL).first()
    log_dir = row.Content

    row=course(GeneralConfig.ConfigItem =='current_config').select(GeneralConfig.ALL).first()
    config_file = row.Content

    # get polling period from config
    polling_period = 30
    open_config_file = open(config_file, "r")
    for line in open_config_file:
        if "server_timeout" in line:
            try:
                polling_period = int(line.split(":")[1])
            except:
                polling_period = 30 
           
    autosub_log = os.path.join(log_dir, "autosub.log")
    log_lines = __tail(autosub_log,20)
    
    # for recent errors approximate interesting number based on polling periode (this is just a guess based on at least 2 entries per polling period)
    error_lines = __tail_error(autosub_log,int(round((60/polling_period*60*24))/1000+1)*2000)
    
    if(__check_running(autosub_log,polling_period+5)):
        if("No Errors found" in error_lines[0]):
                vels_status = "Up and running"
                vels_status_color = "green"
        else:
                vels_status = "Up and running with recent errors"
                vels_status_color = "yellow"
    else:
        vels_status = "Down or paused"
        vels_status_color = "red"

    return_dict ={'course_name':course_name, 'log_lines': log_lines,'error_lines':error_lines,'vels_status':vels_status, 'vels_status_color':vels_status_color}

    return return_dict

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())
