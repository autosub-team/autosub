# Please verify that VELS_OB Swagger client is copied into web2py/site-packages/swagger_client
import swagger_client as api_vels_ob
from swagger_client.rest import ApiException

def __list_plugins(returnDict):

    #####
    # create list of all active plugins
    #####

    rows=course().select(PluginData.ALL)
    array=[]
    unique_plugins = []
    parameterDict = dict({})

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
    __list_plugins(returnDict)
    __assemble_plugin('vels_ob', returnDict)
    return returnDict

@auth.requires_permission('edit data')
def delete():
    returnDict={}
    __list_plugins(returnDict)
    # HTTP Parameter
    UserId= request.vars['UserId']

    # Config Parameter
    MelodiURL = returnDict.get("PluginParameter").get("vels_ob").get("server")
    MelodiPort = returnDict.get("PluginParameter").get("vels_ob").get("port")
    MelodiPassword = returnDict.get("PluginParameter").get("vels_ob").get("password")

    # Swagger Client config
    api_con = api_vels_ob.Configuration()
    api_con.host = "{}:{}/api".format(MelodiURL, MelodiPort)
    api_con.api_key_prefix['Authorization'] = 'Bearer'

    # Swagger Client instance creation
    auth_instance = api_vels_ob.AuthApi(api_vels_ob.ApiClient(api_con))
    task_instance = api_vels_ob.TaskApi(api_vels_ob.ApiClient(api_con))

    # TODO handle admin username
    payload = api_vels_ob.AuthDetails(email="string", password=MelodiPassword)
    try:
        result = auth_instance.user_login(payload)
        api_con.api_key['Authorization'] = result.authorization

        deleted_task = task_instance.delete_a_task(UserId)
    except ApiException as e:
        #print("Exception: %s\n" % e)
        redirect(URL('index', vars=dict(error=str(e))))
    redirect(URL('index'))
    
