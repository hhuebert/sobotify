#from asyncio import subprocess
import os
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
import subprocess
import shutil
import sounddevice
import pandas
import datetime
import psutil

MainWindow = Tk()
MainWindow.title("Sobotify App")


project_path_default     = os.path.join(os.path.expanduser("~"),".sobotify","projects") # 'path to movement/speech data')

DEFAULT_ROBOT_IP="192.168.0.141"
DEFAULT_ROBOT_NAMES=("stickman","pepper","nao")
DEFAULT_NEW_PROJECT_NAME=("MyProject")

if os.path.isfile(os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")
elif os.path.isfile(os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")
else :
	print ("Cannot find Conda executable path. Abort")
	exit()


class sound_devices(object):

	def __init__(self):
		self.device_dict={}

	def read_device_list(self):
		self.device_dict.clear()
		for index,device in enumerate(sounddevice.query_devices()):
			if device["max_input_channels"]>0:
				#print (f"index:{index}, name:{device['name']}")
				self.device_dict[device['name']]=index
		#print (self.device_dict)

	def get_list(self):
		self.read_device_list()
		device_list=list(self.device_dict.keys())
		return device_list

	def get_device_id(self,device_name):
		#print (self.device_dict[device_name])
		return self.device_dict[device_name]


def get_projects() :
	projects=[]
	project_files = os.listdir(project_path_default)
	for project in project_files:
		projectname ,ext = os.path.splitext(project)
		if ext==".xlsx":
			projects.append(projectname)
	return projects

def get_project_file_name(project_name):
	return os.path.join(project_path_default,str(project_name)+".xlsx")

def get_deleted_project_file_name(project_name):
	return os.path.join(project_path_default,"trash",str(project_name)+".xlsx")

def get_project_info(project_name) :
	data=pandas.read_excel(get_project_file_name(project_name))
	app=str(data.iloc[0,4]).strip()
	language=str(data.iloc[2,4]).strip()
	#print(app)
	#print(language)
	return app,language


class SobotifyAppGui(object):
	
	def __init__(self):
		self.project_proc=None

		self.robot_IP=StringVar()
		self.robot_IP.set(DEFAULT_ROBOT_IP)
		self.robot_IP.trace_add("write",self.check_IP)

		self.sound_devs=sound_devices()
		self.selected_sound_device=StringVar()
		self.sound_devices=self.sound_devs.get_list()
		self.selected_sound_device.set(self.sound_devices[0])

		self.robots=(DEFAULT_ROBOT_NAMES)
		self.selected_robot=StringVar()
		self.selected_robot.set(self.robots[0])

		self.selected_delete_project=StringVar()
		self.selected_curr_project=StringVar()
		self.selected_base_project=StringVar()
		self.new_project=StringVar()

		self.projects=get_projects()
		if len(self.projects)==0:
			self.selected_curr_project.set("")
			self.selected_base_project.set("")
		else:
			self.selected_curr_project.set(self.projects[0])
			self.selected_base_project.set(self.projects[0])
		self.new_project.set(DEFAULT_NEW_PROJECT_NAME)
		self.selected_delete_project.set("")

		self.app,self.language=get_project_info(self.selected_curr_project.get())

		# column 1
		col=1
		padx=5
		Label(MainWindow, text="________________________ settings ________________________").grid(row=1, column=col,padx=padx,pady=5,columnspan=2)

		Label(MainWindow, text="").grid(row=1, column=col,padx=padx,pady=5)
		Label(MainWindow, text="robot name",justify=RIGHT,anchor="e").grid(row=2, column=col,padx=padx,pady=5,sticky=E)
		Label(MainWindow, text="robot IP  ",justify=RIGHT,anchor="e").grid(row=3, column=col,padx=padx,pady=5,sticky=E)
		Label(MainWindow, text="sound device",justify=RIGHT,anchor="e").grid(row=4, column=col,padx=padx,pady=5,sticky=E)

		# column 2
		col=2
		self.combobox_robot_sel=Combobox(MainWindow,textvariable=self.selected_robot)
		self.combobox_robot_sel.grid(sticky="W",row=2, column=col,padx=padx,pady=5)
		self.combobox_robot_sel['values']=self.robots
		self.combobox_robot_sel['width']=30
		self.combobox_robot_sel['state']='readonly'

		Entry(MainWindow, text="IP", textvariable=self.robot_IP, width=15).grid(row=3, column=col,padx=0,pady=20)

		self.combobox_sound_dev_sel=Combobox(MainWindow,textvariable=self.selected_sound_device)
		self.combobox_sound_dev_sel.grid(sticky="W",row=4, column=col,padx=padx,pady=5)
		self.combobox_sound_dev_sel['values']=self.sound_devices
		self.combobox_sound_dev_sel['width']=30
		self.combobox_sound_dev_sel['state']='readonly'

		# column 3-4
		col=3
		Label(MainWindow, text="________________ project ________________").grid(row=1, column=col,padx=20,pady=5,columnspan=2)

		self.combobox_curr_project_sel=Combobox(MainWindow,textvariable=self.selected_curr_project)
		self.combobox_curr_project_sel.grid(sticky="W",row=2, column=col,padx=20,pady=5,columnspan=2)
		self.combobox_curr_project_sel['values']=self.projects
		self.combobox_curr_project_sel['width']=30
		self.combobox_curr_project_sel['state']='readonly'

		Button(MainWindow, text="start", command=self.start_project).grid(row=3, column=col,padx=20,pady=5)
		Button(MainWindow, text="edit", command=self.edit_project).grid(row=4, column=col,padx=20,pady=5)

		col=4
		Button(MainWindow, text="stop", command=self.stop_project).grid(row=3, column=col,padx=20,pady=5)
		Button(MainWindow, text="new/delete...", command=self.new_delete_project).grid(row=4, column=col,padx=20,pady=5)

	def check_IP(self,*args):
		IP_parts=self.robot_IP.get().split(".")
		for IP_part in IP_parts:
			if IP_part.isnumeric():
				if int(IP_part) in range(0,255):
					#print(f"IP {IP_part} is ok")
					pass 
				else: 
					#print(f"IP {IP_part} is out of range")
					return False
			else:
				#print(f"IP {IP_part} is not a number")
				return False
		return True

	def update_project_list(self, deleted_project_name="") :
			self.projects=get_projects()	
			self.combobox_delete_project['values']=self.projects
			self.combobox_base_project['values']=self.projects
			self.combobox_curr_project_sel['values']=self.projects
			self.combobox_delete_project.set("")
			if deleted_project_name==self.selected_curr_project.get() :
				if len(self.projects)==0:
					self.selected_curr_project.set("")
				else:
					self.selected_curr_project.set(self.projects[0])
			if deleted_project_name==self.selected_base_project.get() :
				if len(self.projects)==0:
					self.selected_base_project.set("")
				else:
					self.selected_base_project.set(self.projects[0])

	def start_project(self) :
		self.app,self.language=get_project_info(self.selected_curr_project.get())
		self.stop_project()
		if self.check_IP()==False:
			messagebox.showerror("Robot IP Address Error",f"Invalid robot IP address:\n{self.robot_IP.get()}\nCorrect format is\n4 numbers in range 0..255,\nseparated by dots, for example\n192.168.0.141")
			return
		sobotify_path=os.path.dirname(os.path.abspath(__file__))
		script_path=os.path.join(sobotify_path,'apps',self.app,self.app+'.py')
		conda_env = "sobotify"
		arguments=[conda_exe]
		arguments.append("run")
		arguments.extend(('-n',conda_env))
		arguments.append("--no-capture-output")
		arguments.append("python")
		arguments.append(script_path)
		arguments.extend(('--robot_name',self.selected_robot.get()))
		arguments.extend(('--robot_ip',self.robot_IP.get()))
		arguments.extend(('--language',self.language))
		arguments.extend(('--sound_device',str(self.sound_devs.get_device_id(self.selected_sound_device.get()))))
		arguments.extend(('--project_file',get_project_file_name(self.selected_curr_project.get())))

		#if debug==True:
		print (*arguments)
		self.project_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
		#self.project_proc=subprocess.Popen(arguments)
		print ('started project app, pid=',self.project_proc.pid)
	
	def stop_project(self):
		if not self.project_proc==None: 
			project_process=psutil.Process(self.project_proc.pid)
			project_children=project_process.children(recursive=True)
			print(project_children)
			for child in project_children:
				try:
					#print(f"kill process {child.name} with pid: {child.pid}")
					child.kill()
				except:
					#print(f"process {child.name} with pid: {child.pid} already finished")					
					pass
			try:
				#print(f"kill process with pid: {self.project_proc.pid}")
				self.project_proc.kill()
			except:
				#print(f"process with pid: {self.project_proc.pid} already finished")					
				pass
		else:
			#print("no process to kill")
			pass
		self.project_proc=None

	def edit_project(self):
		arguments=["start"]
		arguments.append(get_project_file_name(self.combobox_curr_project_sel.get()))
		print(arguments)
		project_editor_proc=subprocess.call(arguments,shell=True)


	def create_project(self):
		src=get_project_file_name(self.selected_base_project.get())
		dest=get_project_file_name(self.new_project.get())
		if os.path.isfile(dest):
			messagebox.showerror('File exists',f'Project {self.new_project.get()} already exists. Choose a different name')	
		else:
			if messagebox.askokcancel('Create Project Copy',f'Project file\n{src}\nwill be copied to\n{dest}\nDo you want to proceed?') == True :	
				shutil.copyfile(src,dest)
		self.update_project_list()

	def delete_project(self):
		src=get_project_file_name(self.selected_delete_project.get())
		dest=get_deleted_project_file_name(self.selected_delete_project.get())
		if os.path.isfile(dest):
			if messagebox.askokcancel('File exists',f'Old project file {dest} already exists and will be overwritten.\nDo you want to proceed?') == True :	
				shutil.move(src,dest)
		else:
			if messagebox.askokcancel('Move file', f'Project file\n{src}\nwill be moved to\n{dest}\nDo you want to proceed?') == True :	
				shutil.move(src,dest)
		self.update_project_list(self.selected_delete_project.get())

	def new_delete_project(self) :
		now=datetime.datetime.now()
		date_time_string=now.strftime("%y%m%d_%H%M%S")
		self.new_project.set(DEFAULT_NEW_PROJECT_NAME+"_"+date_time_string)
		ProjectWindow = Toplevel(MainWindow)
		ProjectWindow.grab_set()
		ProjectWindow.title("Create or delete a project")

		col=1
		Label(ProjectWindow, text="name of new project:").grid(row=1, column=col,padx=20,pady=5,)
		Entry(ProjectWindow, text="Entry", textvariable=self.new_project, width=50).grid(row=2, column=col,padx=20,pady=5)
		self.combobox_base_project=Combobox(ProjectWindow,textvariable=self.selected_base_project)
		Label(ProjectWindow, text="name of project to be deleted:",justify=RIGHT,anchor="e").grid(row=3, column=col,padx=20,pady=5,sticky=E)

		col=2
		Label(ProjectWindow, text="based on project:").grid(row=1, column=col,padx=20,pady=5,)
		self.combobox_base_project.grid(sticky="W",row=2, column=col,padx=20,pady=5)
		self.combobox_base_project['values']=self.projects
		self.combobox_base_project['state']='readonly'
		self.combobox_delete_project=Combobox(ProjectWindow,textvariable=self.selected_delete_project)
		self.combobox_delete_project.grid(sticky="W",row=3, column=col,padx=20,pady=20)
		self.combobox_delete_project['values']=self.projects
		self.combobox_delete_project['state']='readonly'

		col=3
		Button(ProjectWindow, text="create new project", command=self.create_project).grid(row=2, column=col,padx=5,pady=5)
		Button(ProjectWindow, text="delete project", command=self.delete_project).grid(row=3, column=col,padx=5,pady=20)


   
sobot_gui=SobotifyAppGui()

MainWindow.mainloop()

