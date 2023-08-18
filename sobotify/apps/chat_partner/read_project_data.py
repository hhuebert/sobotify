import pandas

TEXT_COL=4
TASK_SIZE=25
MAX_NUMBER_OF_TASKS=20
MAX_NUMBER_OF_ALTERNATIVES=25
SETTINGS_OFFSET=0
GENERAL_INFO_OFFSET=10
TASKS_OFFSET=35

def getRow(data,row) :
    keyword=[]
    for col in range(2,MAX_NUMBER_OF_ALTERNATIVES) :
        content=str(data.iloc[row,col]).strip()
        if not content=="":
            keyword.append(content)
    return keyword

def get_project_settings(xls_file_name) :
    data=pandas.read_excel(xls_file_name)
    data.fillna("",inplace=True)
    project_settings={}
    app=str(data.iloc[SETTINGS_OFFSET,TEXT_COL]).strip()
    project_settings["app"]=app

    version=str(data.iloc[SETTINGS_OFFSET+1,TEXT_COL]).strip()
    project_settings["version"]=version

    language=str(data.iloc[SETTINGS_OFFSET+2,TEXT_COL]).strip()
    project_settings["language"]=language

    return project_settings

def get_project_info(xls_file_name) :
    data=pandas.read_excel(xls_file_name)
    data.fillna("",inplace=True)
    general_info={}

    general_info["llm_name"]             =str(data.iloc[GENERAL_INFO_OFFSET,TEXT_COL]).strip()
    general_info["llm_options"]          =str(data.iloc[GENERAL_INFO_OFFSET+1,TEXT_COL]).strip()
    general_info["welcome"]              =str(data.iloc[GENERAL_INFO_OFFSET+2,TEXT_COL]).strip()
    general_info["farewell"]             =str(data.iloc[GENERAL_INFO_OFFSET+3,TEXT_COL]).strip()
    general_info["key_word_intro"]       =str(data.iloc[GENERAL_INFO_OFFSET+4,TEXT_COL]).strip()
    general_info["key_word"]             =str(data.iloc[GENERAL_INFO_OFFSET+5,TEXT_COL]).strip()
    general_info["query_intro"]          =str(data.iloc[GENERAL_INFO_OFFSET+6,TEXT_COL]).strip()
    general_info["reply_intro"]          =str(data.iloc[GENERAL_INFO_OFFSET+7,TEXT_COL]).strip()

    return general_info


