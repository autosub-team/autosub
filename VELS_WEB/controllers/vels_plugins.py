def __list_plugins():

    #####
    # create list of all active plugins
    #####

    rows=course().select(PluginData.ALL)
    array=[]
    unique_plugins = []
    parameterDict = dict({})
    returnDict = dict({})

    for row in rows:
        if(row.PluginName not in unique_plugins):
            unique_plugins.append(row.PluginName)
            current_plugin = []
            for subrow in rows:
                if(unique_plugins[-1] == subrow.PluginName):
                    current_plugin.append(subrow.ParameterName)
            parameterDict.update({row.PluginName : current_plugin})
        parameterDict.update({row.PluginName : current_plugin})

    returnDict.update({'PluginParameter' : parameterDict})
    returnDict.update({'ActivePlugins' : unique_plugins} )

    return returnDict

def __assemble_plugin(plugin_name):

    #####
    # set entries for each plugin
    # plugin_active controls if plugin is visible at VELS_WEB
    # plugin_active has to be set for every possible plugin
    #####
    returnDict={}

    #if(plugin_name == 'vels_ob'):
     #   returnDict.update({'vels_ob_active': True})

    return returnDict


@auth.requires_permission('view data')
def index():
    returnDict={}
    returnDict.update(__list_plugins())
    
    returnDict.update(__assemble_plugin('vels_ob'))
    return returnDict

#@auth.requires_permission('edit data')
#def delete():
#    TaskNr= request.vars['TaskNr']
#    UserId= request.vars['UserId']
#    if semester( (UserTasks.TaskNr==TaskNr) & (UserTasks.UserId==UserId) ).delete():
#        msg='Deletion of UserTask with UserId/TaskNr'+UserId+'/'+TaskNr+' succeded' 
#    else:
#        msg='Deletion of UserTask with UserId/TaskNr'+UserId+'/'+TaskNr+' failed'
 #   redirect(URL('index'))
    
