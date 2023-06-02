import pandas

TEXT_COL=4
TASK_SIZE=10
MAX_NUMBER_OF_TASKS=50
MAX_NUMBER_OF_ALTERNATIVES=8
SETTINGS_OFFSET=0
GENERAL_INFO_OFFSET=10
TASKS_OFFSET=20

def getKeyword(data,row) :
    keyword=[]
    for col in range(2,MAX_NUMBER_OF_ALTERNATIVES) :
        content=str(data.iloc[row,col]).strip()
        if not content=="":
            keyword.append(content)
    return keyword

def getTask(data,index):
    task={}
    question=data.iloc[index+0,TEXT_COL]
    question2=data.iloc[index+1,TEXT_COL]
    answer=data.iloc[index+2,TEXT_COL]
    keyword1=getKeyword(data,index+3)
    keyword2=getKeyword(data,index+4)
    keyword3=getKeyword(data,index+5)
    keyword4=getKeyword(data,index+6)
    if not question.strip()=="" :
        task["question"]=question    
        task["question2"]=question2
        task["answer"]=answer
        answers=[]
        answers.append(keyword1)
        if not len(keyword2)==0:
            answers.append(keyword2)
        if not len(keyword3)==0:
            answers.append(keyword3)
        if not len(keyword3)==0:
            answers.append(keyword4)
        task["answers"]=answers
    return task




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

def get_general_info(xls_file_name) :
    data=pandas.read_excel(xls_file_name)
    data.fillna("",inplace=True)
    general_info={}
    reception=str(data.iloc[GENERAL_INFO_OFFSET,TEXT_COL]).strip()
    general_info["welcome"]=reception

    farewell=str(data.iloc[GENERAL_INFO_OFFSET+1,TEXT_COL]).strip()
    general_info["farewell"]=farewell

    correct_answer=str(data.iloc[GENERAL_INFO_OFFSET+2,TEXT_COL]).strip()
    general_info["correct"]=correct_answer

    incorrect_answer=str(data.iloc[GENERAL_INFO_OFFSET+3,TEXT_COL]).strip()
    general_info["incorrect"]=incorrect_answer

    score=str(data.iloc[GENERAL_INFO_OFFSET+4,TEXT_COL]).strip()
    general_info["score"]=score

    noanswer=str(data.iloc[GENERAL_INFO_OFFSET+5,TEXT_COL]).strip()
    general_info["noanswer"]=noanswer

    return general_info

def get_tasks(xls_file_name) :
    data=pandas.read_excel(xls_file_name)
    data.fillna("",inplace=True)

    tasks=[]
    for tasknum in range (0,MAX_NUMBER_OF_TASKS-1) :
        task=getTask(data,TASKS_OFFSET+tasknum*TASK_SIZE)
        if not len(task)==0:
            tasks.append(task)
    return tasks
