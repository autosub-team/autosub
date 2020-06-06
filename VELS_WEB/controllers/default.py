import os

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

@auth.requires_login()
def index():
    row=course(GeneralConfig.ConfigItem =='course_name').select(GeneralConfig.ALL).first()
    course_name = row.Content

    row=course(GeneralConfig.ConfigItem =='log_dir').select(GeneralConfig.ALL).first()
    log_dir = row.Content

    autosub_log = os.path.join(log_dir, "autosub.log")
    log_lines = __tail(autosub_log,20)

    return_dict ={'course_name':course_name, 'log_lines': log_lines}

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
