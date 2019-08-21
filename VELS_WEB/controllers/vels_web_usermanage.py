val={'username'  : [IS_NOT_EMPTY()],
     'first_name': [IS_NOT_EMPTY()],
     'last_name' : [IS_NOT_EMPTY()],
     'email'     : [IS_NOT_EMPTY(),IS_EMAIL()],
     'password'  : [IS_STRONG(entropy=50.0)]}

def __entries():
    rows=authdb().select(auth_user.ALL)
    array=[]
    for row in rows:
        user_id = row.id
        role_row = authdb((auth_user.id == user_id)&(auth_membership.user_id == user_id)&\
                          (auth_group.id==auth_membership.group_id)).select(auth_group.ALL).first()

        group = role_row.role

        entry={'id'         : row.id,
               'username'   : row.username,
               'first_name' : row.first_name,
               'last_name'  : row.last_name,
               'email'      : row.email,
               'group'      : group}
        array.append(entry)

    return dict(entries=array)

def __existing_groups():
    group_names = []
    group_ids = []

    groups = authdb().select(auth_group.ALL)
    for row in groups:
        group_names.append(row.role)
        group_ids.append(int(row.id))

    return (group_ids, group_names)

@auth.requires_permission('manage users')
def index():
    returnDict={}
    returnDict.update(__entries())
    return returnDict

@auth.requires_permission('manage users')
def newUser():
    returnDict={}

    (group_ids, group_names) = __existing_groups()

    inputs=TD(INPUT(_name='username',  requires= val['username'])), \
           TD(INPUT(_name='first_name',  requires= val['first_name'])),\
           TD(INPUT(_name='last_name',   requires= val['last_name'])),\
           TD(INPUT(_name='email',       requires= val['email'],_size="30")),\
           TD(SELECT(_name='group', *group_names)),\
           TD(INPUT(_name='password', _type="password", requires=val['password'])),\
           TD(INPUT(_type='submit',_label='Save'))
    form=FORM(inputs)

    if(form.process().accepted):
        user_id = auth_user.insert(username = form.vars.username,
                                   first_name = form.vars.first_name,
                                   last_name = form.vars.last_name,
                                   email = form.vars.email,
                                   password = authdb.auth_user.password.requires[0](form.vars.password)[0])

        group_id = group_ids[group_names.index(form.vars.group)]
        auth.add_membership(group_id, user_id)

        redirect(URL('index'))

    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

@auth.requires_permission('manage users')
def deleteUser():
    user_id = request.vars['user_id']

    if authdb(auth_user.id==user_id).delete() :
        row = authdb(auth_membership.user_id == user_id).select(auth_membership.ALL).first()
        if row:
            group_id = row.group_id
            auth.del_membership(group_id, user_id)
        msg='User' + user_id + ' deleted'
    else:
        msg='User' + user_id + ' delete failed'
    redirect(URL('index'))

@auth.requires_permission('manage users')
def editUser():
    user_id = int(request.vars['user_id'])
    (group_ids, group_names) = __existing_groups()

    returnDict={}

    entry = authdb(auth_user.id == user_id).select(auth_user.ALL).first()

    row = authdb(auth_membership.user_id == user_id).select(auth_membership.ALL).first()
    if row:
        group_id = row.group_id
        group_name = group_names[group_ids.index(group_id)]

    inputs=TD(INPUT(_name='username',  requires= val['username'], _value=entry.username)), \
           TD(INPUT(_name='first_name',  requires= val['first_name'], _value = entry.first_name)),\
           TD(INPUT(_name='last_name',   requires= val['last_name'], _value = entry.last_name)),\
           TD(INPUT(_name='email',       requires= val['email'], _value = entry.email ,_size="30")),\
           TD(SELECT(_name='group', *group_names, value = group_name)),\
           TD(INPUT(_type='submit',_label='Save'))

    form=FORM(inputs)

    if(form.process().accepted):
        cur_group = group_id
        new_group = group_ids[group_names.index(form.vars.group)]
        if cur_group != new_group:
            auth.del_membership(cur_group, user_id)
            auth.add_membership(new_group, user_id)

        authdb(auth_user.id==user_id).update(username = form.vars.username,
                                   first_name = form.vars.first_name,
                                   last_name = form.vars.last_name,
                                   email = form.vars.email)

        redirect(URL('index'))

    returnDict.update({'editUserId':user_id})
    returnDict.update({'form':form})
    returnDict.update(__entries())

    return returnDict

@auth.requires_permission('manage users')
def setPassword():
    user_id = int(request.vars['user_id'])
    row = authdb(auth_user.id == user_id).select(auth_user.ALL).first()

    username = row.username
    first_name = row.first_name
    last_name = row.last_name

    user_data = {'username'   : username,
                 'first_name' : first_name,
                 'last_name'  : last_name,
                 'user_id'    : user_id}

    inputs = "Password: ",INPUT(_name='password', _type="password", requires=val['password']),\
             INPUT(_type='submit',_label='Set Password')
    form = FORM(inputs)

    if(form.process().accepted):
        authdb(auth_user.id==user_id).update(\
            password = authdb.auth_user.password.requires[0](form.vars.password)[0])
        redirect(URL('index'))

    returnDict = {}
    returnDict.update({'form':form})
    returnDict.update(user_data)
    return returnDict
