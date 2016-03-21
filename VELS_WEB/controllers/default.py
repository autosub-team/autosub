def index():
    row=course(GeneralConfig.ConfigItem =='course_name').select(GeneralConfig.ALL).first()
    return_dict ={'course_name':row.Content}
    return return_dict
