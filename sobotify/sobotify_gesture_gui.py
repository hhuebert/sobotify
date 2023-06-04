#from asyncio import subprocess
import os
import sys
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog
import subprocess
import shutil
import psutil

MainWindow = Tk()
MainWindow.title("Sobotify Gesture")

data_path_default        = os.path.join(os.path.expanduser("~"),".sobotify","data") # 'path to movement/speech data')

DEFAULT_ROBOT_IP="192.168.0.141"
DEFAULT_ROBOT_NAMES=("stickman","pepper","nao")
DEFAULT_NEW_PROJECT_NAME=("MyGesture")
DEFAULT_LANGUAGES=("german","english")

if os.path.isfile(os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"miniconda3","condabin","conda.bat")
elif os.path.isfile(os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")):
	conda_exe=os.path.join(os.path.expanduser("~"),"AppData","Local","miniconda3","condabin","conda.bat")
else :
	print ("Cannot find Conda executable path. Abort")
	exit()

def get_gestures() :
	gestures=[]
	gesture_files = os.listdir(data_path_default)
	for gesture in gesture_files:
		gesture_name ,ext = os.path.splitext(gesture)
		if ext==".srt":
			gestures.append(gesture_name)
	return gestures

def get_gesture_file_name(gesture_name):
	return os.path.join(data_path_default,str(gesture_name)+".srt")

def get_deleted_gesture_file_name(gesture_name):
	return os.path.join(data_path_default,"trash",str(gesture_name)+".srt")

class SobotifyGestureGui(object):
	
	def __init__(self):
		self.gesture_proc=None
		self.extract_proc=None

		self.robot_IP=StringVar()
		self.robot_IP.set(DEFAULT_ROBOT_IP)
		self.robot_IP.trace_add("write",self.check_IP)


		self.languages=(DEFAULT_LANGUAGES)
		self.selected_language=StringVar()
		self.selected_language.set(self.languages[0])

		self.selected_language_extract=StringVar()
		self.selected_language_extract.set(self.languages[0])

		self.robots=(DEFAULT_ROBOT_NAMES)
		self.selected_robot=StringVar()
		self.selected_robot.set(self.robots[0])

		self.selected_delete_gesture=StringVar()
		self.selected_curr_gesture=StringVar()
		self.new_gesture=StringVar()

		self.gestures=get_gestures()
		if len(self.gestures)==0:
			self.selected_curr_gesture.set("")
		else:
			self.selected_curr_gesture.set(self.gestures[0])
		self.new_gesture.set(DEFAULT_NEW_PROJECT_NAME)
		self.selected_delete_gesture.set("")

		self.video_file=StringVar()
		self.video_file.set("gesture_video.mp4")

		# column 1
		col=1
		padx=5
		Label(MainWindow, text="_______________________ settings _______________________").grid(row=1, column=col,padx=padx,pady=5,columnspan=2)

		Label(MainWindow, text="").grid(row=1, column=col,padx=padx,pady=5)
		Label(MainWindow, text="robot name",justify=RIGHT,anchor="e").grid(row=2, column=col,padx=padx,pady=5,sticky=E)
		Label(MainWindow, text="robot IP  ",justify=RIGHT,anchor="e").grid(row=3, column=col,padx=padx,pady=5,sticky=E)
		Label(MainWindow, text="language",justify=RIGHT,anchor="e").grid(row=4, column=col,padx=padx,pady=5,sticky=E)

		# column 2
		col=2
		self.combobox_robot_sel=Combobox(MainWindow,textvariable=self.selected_robot)
		self.combobox_robot_sel.grid(sticky="W",row=2, column=col,padx=padx,pady=5)
		self.combobox_robot_sel['values']=self.robots
		self.combobox_robot_sel['width']=30
		self.combobox_robot_sel['state']='readonly'

		Entry(MainWindow, text="IP", textvariable=self.robot_IP, width=15).grid(row=3, column=col,padx=0,pady=20)

		self.combobox_language_sel=Combobox(MainWindow,textvariable=self.selected_language)
		self.combobox_language_sel.grid(sticky="W",row=4, column=col,padx=padx,pady=5)
		self.combobox_language_sel['values']=self.languages
		self.combobox_language_sel['width']=30
		self.combobox_language_sel['state']='readonly'


		# column 3-4
		col=3
		padx=5
		Label(MainWindow, text="_____________________________ gesture _____________________________").grid(row=1, column=col,padx=padx,pady=5,columnspan=3)

		self.combobox_curr_gesture_sel=Combobox(MainWindow,textvariable=self.selected_curr_gesture)
		self.combobox_curr_gesture_sel.grid(sticky="W",row=2, column=col,padx=padx,pady=5,columnspan=2)
		self.combobox_curr_gesture_sel['values']=self.gestures
		self.combobox_curr_gesture_sel['width']=40
		self.combobox_curr_gesture_sel['state']='readonly'

		Button(MainWindow, text="start", command=self.start_gesture).grid(row=3, column=col,padx=0,pady=5)
		Button(MainWindow, text="edit", command=self.edit_gesture).grid(row=4, column=col,padx=0,pady=5)

		col=4
		Button(MainWindow, text="stop", command=self.stop_gesture).grid(row=3, column=col,padx=0,pady=5)
		Button(MainWindow, text="add/delete...", command=self.new_delete_gesture).grid(row=4, column=col,padx=0,pady=5)

		col=5
		Button(MainWindow, text="reload", command=self.update_gesture_list).grid(row=2, column=col,padx=0,pady=5)

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

	def update_gesture_list(self, deleted_project_name="") :
			self.projects=get_gestures()	
			self.combobox_curr_gesture_sel['values']=self.projects
			try:
				self.combobox_delete_gesture['values']=self.projects
				self.combobox_delete_gesture.set("")
			except:
				pass
			if deleted_project_name==self.selected_curr_gesture.get() :
				if len(self.gestures)==0:
					self.selected_curr_gesture.set("")
				else:
					self.selected_curr_gesture.set(self.gestures[0])


	def start_gesture(self):
		sobotify_path=os.path.dirname(os.path.abspath(__file__))
		script_path=os.path.join(sobotify_path,'robotcontrol','robotcontrol.py')
		if self.selected_robot.get().lower() == "pepper" or self.selected_robot.get().lower() == "nao" :
			conda_env = "sobotify_naoqi"
		else : 
			conda_env = "sobotify" 
		arguments=[conda_exe]
		arguments.append("run")
		arguments.extend(('-n',conda_env))
		arguments.append("--no-capture-output")
		arguments.append("python")
		arguments.append(script_path)
		arguments.extend(('--robot_name',self.selected_robot.get()))
		arguments.extend(('--robot_ip',self.robot_IP.get()))
		arguments.extend(('--language',self.selected_language.get()))
		arguments.extend(('--gesture',self.selected_curr_gesture.get()))
		print (*arguments)
		self.gesture_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)
		#rocontrol_proc=subprocess.Popen(arguments)
		print ('started robot controller, pid=',self.gesture_proc.pid)
	
	def stop_gesture(self):
		if not self.gesture_proc==None: 
			gesture_process=psutil.Process(self.gesture_proc.pid)
			gesture_children=gesture_process.children(recursive=True)
			print(gesture_children)
			for child in gesture_children:
				try:
					print(f"kill process {child.name} with pid: {child.pid}")
					child.kill()
				except:
					print(f"process {child.name} with pid: {child.pid} already finished")					
			try:
				print(f"kill process with pid: {self.gesture_proc.pid}")
				self.gesture_proc.kill()
			except:
				print(f"process with pid: {self.gesture_proc.pid} already finished")					
		else:
			print("no process to kill")
		self.gesture_proc=None

	def edit_gesture(self):
		arguments=["notepad.exe"]
		arguments.append(get_gesture_file_name(self.combobox_curr_gesture_sel.get()))
		print(arguments)
		self.gesture_editor_proc=subprocess.Popen(arguments,creationflags=subprocess.CREATE_NEW_CONSOLE)


	def extract_gesture(self):
		dest=get_gesture_file_name(self.new_gesture.get())
		if os.path.isfile(dest):
			if messagebox.askokcancel('File exists',f'gesture {self.new_gesture.get()} already exists and will be overwritten.\nDo you want to proceed?') == False :	
				return
		sobotify_path=os.path.dirname(os.path.abspath(__file__))
		arguments=[sys.executable,os.path.join(sobotify_path,'tools','extract','extract.py')]
		arguments.extend(('--video_file',self.video_file.get()))
		arguments.extend(('--robot_name',"all"))
		arguments.extend(('--language',self.selected_language_extract.get()))
		print (*arguments)
		self.extract_proc=subprocess.Popen(arguments)
		print ('started gesture/speech analysis, pid=',self.extract_proc.pid)
		self.update_gesture_list(self.selected_delete_gesture.get())

	def stop_extract(self):
		if not self.extract_proc==None: 
			extract_process=psutil.Process(self.extract_proc.pid)
			extract_children=extract_process.children(recursive=True)
			print(extract_children)
			for child in extract_children:
				try:
					#print(f"kill process {child.name} with pid: {child.pid}")
					child.kill()
				except:
					#print(f"process {child.name} with pid: {child.pid} already finished")
					pass					
			try:
				#print(f"kill process with pid: {self.extract_proc.pid}")
				self.extract_proc.kill()
			except:
				#print(f"process with pid: {self.extract_proc.pid} already finished")					
				pass					
		else:
			#print("no process to kill")
			pass					
		self.extract_proc=None

	def delete_gesture(self):
		src=get_gesture_file_name(self.selected_delete_gesture.get())
		dest=get_deleted_gesture_file_name(self.selected_delete_gesture.get())
		if os.path.isfile(dest):
			if messagebox.askokcancel('File exists',f'Existing gesture file\n{dest}\nwill be overwritten.\nDo you want to proceed?') == True :	
				shutil.move(src,dest)
		else:
			if messagebox.askokcancel('Move file', f'Gesture file\n{src}\nwill be moved to\n{dest}\nDo you want to proceed?') == True :	
				shutil.move(src,dest)
		self.update_gesture_list(self.selected_delete_gesture.get())

	def select_video_file(self) :
		file_name=filedialog.askopenfilename();
		self.video_file.set(file_name)
		base_file_name, ext = os.path.splitext(os.path.basename(file_name))
		self.new_gesture.set(base_file_name)

	def select_video_file(self) :
		file_name=filedialog.askopenfilename();
		self.video_file.set(file_name)
		base_file_name, ext = os.path.splitext(os.path.basename(file_name))
		self.new_gesture.set(base_file_name)

	def new_delete_gesture(self) :
		self.new_gesture.set("")
		ProjectWindow = Toplevel(MainWindow)
		ProjectWindow.grab_set()
		ProjectWindow.title("Add or delete a gesture")
		self.update_gesture_list(self.selected_delete_gesture.get())

		padx=5
		col=1
		Label(ProjectWindow, text="add:",justify=RIGHT,anchor="e").grid(row=1, column=col,padx=padx,pady=5,sticky=E)
		Label(ProjectWindow, text="delete:",justify=RIGHT,anchor="e").grid(row=2, column=col,padx=padx,pady=20,sticky=E)

		col=2
		Button(ProjectWindow, text="select video file", command=self.select_video_file).grid(row=1, column=col,padx=padx,pady=5)
		Label(ProjectWindow, text="gesture:",justify=RIGHT,anchor="e").grid(row=2, column=col,padx=padx,pady=20,sticky=E)

		col=3
		Entry(ProjectWindow, text="Entry", textvariable=self.new_gesture, width=40, state=DISABLED).grid(row=1, column=col,padx=padx,pady=5)
		self.combobox_delete_gesture=Combobox(ProjectWindow,textvariable=self.selected_delete_gesture)
		self.combobox_delete_gesture.grid(sticky="W",row=2, column=col,padx=padx,pady=20)
		self.combobox_delete_gesture['values']=self.gestures
		self.combobox_delete_gesture['state']='readonly'
		self.combobox_delete_gesture['width']=40

		col=4
		self.combobox_language_sel=Combobox(ProjectWindow,textvariable=self.selected_language_extract)
		self.combobox_language_sel.grid(sticky="W",row=1, column=col,padx=0,pady=5)
		self.combobox_language_sel['values']=self.languages
		self.combobox_language_sel['state']='readonly'
		Button(ProjectWindow, text="reload", command=self.update_gesture_list).grid(row=2, column=col,padx=0,pady=5,sticky=W)


		col=5
		Button(ProjectWindow, text="add gesture", command=self.extract_gesture).grid(row=1, column=col,padx=padx,pady=5)
		Button(ProjectWindow, text="delete  gesture", command=self.delete_gesture).grid(row=2, column=col,padx=padx,pady=20)

		col=6
		Button(ProjectWindow, text="... abort", command=self.stop_extract).grid(row=1, column=col,padx=padx,pady=5)

		self.update_gesture_list(self.selected_delete_gesture.get())


sobot_gesture_gui=SobotifyGestureGui()

MainWindow.mainloop()

