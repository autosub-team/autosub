# Please verify that VELS_OB Swagger client is copied into web2py/site-packages/swagger_client
import swagger_client as api_vels_ob

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
            current_plugin = dict({})
            for subrow in rows:
                if(unique_plugins[-1] == subrow.PluginName):
                    current_plugin.update({subrow.ParameterName : subrow.Value})
                
            parameterDict.update({row.PluginName : current_plugin})
        parameterDict.update({row.PluginName : current_plugin})

    returnDict.update({'PluginParameter' : parameterDict})
    returnDict.update({'ActivePlugins' : unique_plugins} )

    return returnDict

def __assemble_plugin(plugin_name, returnDict):

    #####
    # set entries for each plugin
    # plugin_active controls if plugin is visible at VELS_WEB
    # plugin_active has to be set for every possible plugin
    #####

    if(plugin_name == 'vels_ob'):
        returnDict.update({'vels_ob_active': True})
        
        MelodiURL = returnDict.get("PluginParameter").get(plugin_name).get("server")
        MelodiPort = returnDict.get("PluginParameter").get(plugin_name).get("port")
        MelodiPassword = returnDict.get("PluginParameter").get(plugin_name).get("password")

        api_con = api_vels_ob.Configuration()
        api_con.host = "{}:{}/api".format(MelodiURL, MelodiPort)
        task_instance = api_vels_ob.TaskApi(api_vels_ob.ApiClient(api_con))
        all_tasks = task_instance.list_of_tasks()
        
        returnDict.update({'vels_ob_tasks': all_tasks})
    return returnDict


@auth.requires_permission('view data')
def index():
    returnDict={}
    returnDict.update(__list_plugins())
    
    __assemble_plugin('vels_ob', returnDict)
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
    
