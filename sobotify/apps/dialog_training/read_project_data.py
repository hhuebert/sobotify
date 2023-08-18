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
        content=str(data.iloc[row,col]) 
        if not content=="":
            keyword.append(content)
    return keyword

def getTask(data,index):
    task={}
    question       = getRow(data,index+0)
    hint           =   data.iloc[index+1,TEXT_COL]
    answer_intro   =   data.iloc[index+2,TEXT_COL]
    answer         =   data.iloc[index+3,TEXT_COL]
    keyword1       = getRow(data,index+4)
    keyword2       = getRow(data,index+5)
    keyword3       = getRow(data,index+6)
    keyword4       = getRow(data,index+7)
    keyword5       = getRow(data,index+8)
    keyword_hint   =   data.iloc[index+9,TEXT_COL]
    grammar        = getRow(data,index+10)
    grammar_hint   =   data.iloc[index+11,TEXT_COL]
    phrase1        = getRow(data,index+12)
    phrase2        = getRow(data,index+13)
    phrase3        = getRow(data,index+14)
    phrase_hint    = data.iloc[index+15,TEXT_COL]
    adjective      = getRow(data,index+16)
    adjective_hint = data.iloc[index+17,TEXT_COL]
    pronunciation1 = getRow(data,index+18)
    pronunciation2 = getRow(data,index+19)
    pronunciation3 = getRow(data,index+20)
    pronunciation_hint = data.iloc[index+21,TEXT_COL]
    print (index)
    if question and not question[0].strip()=="" :
        print (question)
        #    "hint3":"1",
        task["question"]=question    
        task["hint1"]=hint
        task["hint3"]=answer_intro
        task["answer"]=answer
        task["keyword_hint"]=keyword_hint
        task["hint2"]=grammar_hint
        task["phrase_hint"]=phrase_hint
        task["adjective_hint"]=adjective_hint
        task["hint4"]=pronunciation_hint
        grammars=[]
        grammars.append(grammar)
        task["grammar1"]=grammars
        adjectives=[]
        adjectives.append(adjective)
        task["adjective"]=adjectives
        keywords=[]
        keywords.append(keyword1)
        if not len(keyword2)==0:
            keywords.append(keyword2)
        if not len(keyword3)==0:
            keywords.append(keyword3)
        if not len(keyword4)==0:
            keywords.append(keyword4)
        if not len(keyword5)==0:
            keywords.append(keyword5)
        task["keywords"]=keywords
        phrases=[]
        phrases.append(phrase1)
        if not len(phrase2)==0:
            phrases.append(phrase2)
        if not len(phrase3)==0:
            phrases.append(phrase3)
        task["phrase"]=phrases
        pronunciations=[]
        pronunciations.append(pronunciation1)
        if not len(pronunciation2)==0:
            pronunciations.append(pronunciation2)
        if not len(pronunciation3)==0:
            pronunciations.append(pronunciation3)
        task["pronunciation1"]=pronunciations
    return task

def get_tasks(xls_file_name,start_num,end_num) :
    data=pandas.read_excel(xls_file_name)
    data.fillna("",inplace=True)

    tasks=[]
    for tasknum in range (start_num-1,end_num) :
        task=getTask(data,TASKS_OFFSET+tasknum*TASK_SIZE)
        if not len(task)==0:
            tasks.append(task)
    return tasks


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

    general_info["welcome"]              =str(data.iloc[GENERAL_INFO_OFFSET,TEXT_COL]).strip()
    general_info["welcome2"]             =str(data.iloc[GENERAL_INFO_OFFSET+1,TEXT_COL]).strip()
    general_info["farewell"]             =str(data.iloc[GENERAL_INFO_OFFSET+2,TEXT_COL]).strip()
    general_info["getstarted"]           =str(data.iloc[GENERAL_INFO_OFFSET+3,TEXT_COL]).strip()
    general_info["perfect_feedback"]       =getRow(data,GENERAL_INFO_OFFSET+4)
    general_info["great_job_feedback"]     =getRow(data,GENERAL_INFO_OFFSET+5)
    general_info["affirmation"]          =str(data.iloc[GENERAL_INFO_OFFSET+6,TEXT_COL]).strip()
    general_info["reply_great"]          =str(data.iloc[GENERAL_INFO_OFFSET+7,TEXT_COL]).strip()
    general_info["full_sentence_request"]=str(data.iloc[GENERAL_INFO_OFFSET+8,TEXT_COL]).strip()
    general_info["once_again"]           =str(data.iloc[GENERAL_INFO_OFFSET+9,TEXT_COL]).strip()
    general_info["getprepared_dialog"]=getRow(data,GENERAL_INFO_OFFSET+10)
    general_info["taskdone"]=getRow(data,GENERAL_INFO_OFFSET+11)
    general_info["task_group_start_no"]=getRow(data,GENERAL_INFO_OFFSET+12)
        

    general_info["happy_emotion_hints"]    = getRow(data,GENERAL_INFO_OFFSET+14)
    general_info["happy_gesture"]          = getRow(data,GENERAL_INFO_OFFSET+15)
    general_info["neutral_emotion_hints"]  = getRow(data,GENERAL_INFO_OFFSET+16)
    general_info["neutral_gesture"]        = getRow(data,GENERAL_INFO_OFFSET+17)
    general_info["sad_emotion_hints"]      = getRow(data,GENERAL_INFO_OFFSET+18)
    general_info["sad_gesture"]            = getRow(data,GENERAL_INFO_OFFSET+19)
    general_info["negative_emotion_hints"] = getRow(data,GENERAL_INFO_OFFSET+20)
    general_info["negative_gesture"]       = getRow(data,GENERAL_INFO_OFFSET+21)
    general_info["intermediate_gesture"]   = getRow(data,GENERAL_INFO_OFFSET+22)

    tasks_groups=[]
    for num,task_group_start_no in enumerate(general_info["task_group_start_no"]):
        print(task_group_start_no)
        start=int(task_group_start_no)
        if num<len(general_info["task_group_start_no"])-1:
            end=int(general_info["task_group_start_no"][num+1])-1
        else:
            end=MAX_NUMBER_OF_TASKS
        print("=================== Task:",num,"question range:",start,"-",end," ===================")
        tasks=get_tasks(xls_file_name,start,end)
        tasks_groups.append(tasks)

    return general_info,tasks_groups


