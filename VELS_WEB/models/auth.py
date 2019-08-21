# -*- coding: utf-8 -*-
authdb = DAL('sqlite://auth.db')

from gluon.tools import Auth
auth = Auth(authdb, signature=False, csrf_prevention = False)
auth.define_tables(username=True, signature=False)
auth.settings.registration_requires_approval = True
auth.settings.create_user_groups = None
auth.settings.actions_disabled.append('register')
auth.settings.actions_disabled.append('request_reset_password')

# Only will be done on first load
if not authdb(authdb.auth_user.id>0).count():
    # create groups
    vels_admin_group = auth.add_group('vels_admin', 'can change settings, can view statistics')
    vels_tutor_group = auth.add_group('vels_tutor', 'can view settings, can view statistics')

    # create initial admin
    fname = "vels_admin"
    lname = "vels_admin"
    email = "invalid@invalid.com"
    username = "vels_admin"
    passwd = "vels_admin"
    hashed_passwd = authdb.auth_user.password.requires[0](passwd)[0]

    initial_admin = authdb.auth_user.insert(first_name=fname,last_name=lname,email=email,
                        password=hashed_passwd, username=username)

    # make initial admin member of group vels_admins
    auth.add_membership(vels_admin_group, initial_admin)

    ##########################################################
    # set the permissions for each group
    ##########################################################
    auth.add_permission(vels_admin_group, 'edit data')
    auth.add_permission(vels_admin_group, 'view data')
    auth.add_permission(vels_admin_group, 'manage users')

    auth.add_permission(vels_tutor_group, 'view data')
    ##########################################################

    # use @auth.requires_permission('view data') for example as function decorator

else:
    pass

auth_user = authdb.auth_user
auth_group = authdb.auth_group
auth_membership = authdb.auth_membership
