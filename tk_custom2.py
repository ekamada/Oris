#An updated version of tk custom library

from Tkinter import *
from PIL import Image,ImageTk

import time

class oris():
	padding=3
	dim="{0}x{1}+0+0" #Syntax for full screen dimensions

	font="Leelawadee"

	def __init__(self,window):
		self.window=window
		self.width=window.winfo_screenwidth()#-self.padding
		self.height=window.winfo_screenheight()#-self.padding
		self.window.geometry(self.dim.format(self.width,self.height))
		self.window.bind('<Escape>',exit)
	
	def exit(self):
		self.window.destroy()

	def get(self):
		return self.window

	def size(self):
		return self.width,self.height

class img():
	def __init__(self,parent,img_path):
		self.parent=parent
		self.image=Image.open(img_path).convert("RGBA")
		self.width=self.image.width-10
		self.height=self.image.height-10
		self.photo=ImageTk.PhotoImage(self.image)

		self.label=Label(self.parent,image=self.photo,width=self.width,height=self.height)
		self.label.image=self.photo
		self.label.pack_propagate(False)
		self.label.pack()

		#self.canvas=Canvas(self.parent,width=w,height=h)
		#self.canvas.config(bd=0,highlightthickness=0)
		#self.canvas.create_image(0,0,anchor=NW,image=self.photo)
		#self.canvas.image=self.photo
		#self.canvas.pack()




class myPage(Tk): # Custom Tkinter object for our windows
   def __init__(self,parent,w,h): #initialize
      self.fsize=25

      self.frame=Frame(parent,width=w,height=h)
      self.frame.config(highlightthickness=1,highlightbackground="black")
      self.frame.grid_propagate(False) #Do not resize to fit widget
      self.frame.grid(row=0,column=0,sticky="nsew")
      self.label=Label(self.frame)
      self.frame.pack_propagate(False)
      self.label.place(relx=0.5,rely=0.5,anchor=CENTER)

   def color(self,bg): # color config
      self.frame.config(bg=bg)
      self.label.config(bg=bg)

   def title(self,text,fg=None):
      if (fg==None):
         self.label.config(text=text,font=(oris.font,self.fsize))
      else:
         self.label.config(text=text,font=(oris.font,self.fsize),fg=fg)

   def font_size(self,size):
	    self.fsize=size

   def show(self,event): # event function to navigate to window
      self.frame.lift()

   def fetch(self):  # used as a reference for buttons to prevent infinite recursion
	   return self.frame



class Btn(): # Custom Tkinter Button because the regular ones dont do what i want
   def __init__(self,root,page,row,col,name):
      self.root=root
      self.h=85
      self.w=175
      self.fsize=30
      self.btn_col="#368cd8"

      self.page=page
      self.frame=Frame(page,height=self.h,width=self.w)
      self.frame.grid(row=row,column=col,padx=10,pady=(8,0))
      #self.frame.config(highlightthickness=1,highlightbackground="black") #Button border
      self.frame.config(highlightthickness=1,highlightbackground="black",bd=4,relief=RAISED)
      self.label=Label(self.frame,text=name,bg=self.btn_col,font=(oris.font,self.fsize))
      self.frame.pack_propagate(False) # do not resize to match text size
      self.label.pack(fill=BOTH,expand=1)

   def title(self,text,fg=None): # Config title message
      if (fg==None):
         self.label.config(text=text,font=(oris.font,self.fsize))
      else:
         self.label.config(text=text,font=(oris.font,self.fsize),fg="white")

   def pad(self,x,y):
      self.frame.grid_configure(padx=x,pady=y)

   def resize(self,w,h):
      self.frame.config(width=w,height=h)

   def font_size(self,size):
      self.label.config(font=(oris.font,size))

   def color(self,bg,fg=None): # color config
      if (fg==None):
        self.frame.config(bg=bg)
        self.label.config(bg=bg)
      else:
        self.frame.config(bg=bg)
        self.label.config(bg=bg,fg=fg)

   def unpress(self):
      self.frame.config(relief=RAISED)

   def press(self):
      self.frame.config(relief=SUNKEN)
      after_id=self.root.after(100,self.unpress) 

   def show(self,p2): # event function to navigate to window
      p2.lift()

   def nextPg(self,page2):
      self.label.bind("<ButtonRelease-1>",lambda event, p2=page2:self.show(p2))

   def cmd(self,callback): # Button action
      self.label.bind("<ButtonRelease-1>",callback)


# tkinter object to split each page up in half. 
# Used for separating buttons from displayed data
class subFrame():                         
   def __init__(self,page,position,width,height):
      self.page=page
      self.right=Frame(page,width=width/2+2,height=height)
      self.right.config(bg="#7fbcf4")
      self.right.grid_propagate(0)
      self.right.grid(row=position[0],column=position[1],sticky=E)
			
      self.left=Frame(page,width=width/2,height=height)
      self.left.config(bg="#7fbcf4")
      self.left.grid_propagate(0)
      self.left.grid(row=position[0],column=position[1],sticky=W)

   def colorRight(self,col):
      self.right.config(bg=col)

   def colorLeft(self,col):
      self.left.config(bg=col)

   def getRight(self):
      return self.right

   def getLeft(self):
      return self.left
    
class box():
   def __init__(self,master,width,height,title=None):
      self.master=master
      self.box=Frame(master,width=width,height=height,bg="grey")
      self.box.config(highlightthickness=1,highlightbackground="black")
      self.box.place(relx=0.47,rely=0.39,anchor=CENTER)
      self.title=Label(self.box,text=title,bg="grey")
      self.title.config(font=(oris.font,30))
      self.box.propagate(0)
      self.title.pack()

   def message(self,text):
	    self.title.pack_forget()
	    self.title.config(text=text)
	    self.title.pack()

   def fetch(self):
      return self.box
       

class info():
   def __init__(self,master,w,h):

      self.bg_col="grey"
      self.master=master
      self.data=Label(master,text="0",bg=self.bg_col)
      self.data.config(font=(oris.font,100))
      #self.data.place(relx=0.4,rely=0.3,anchor=CENTER) #relx/relxy are the relative position in the frame (0.5=half the frame)

      self.title=Label(master,text="Recording",bg=self.bg_col)
      self.title.config(font=(oris.font,30))
      #self.title.place(relx=0.4,rely=0.47,anchor=CENTER)

      self.data_box=box(self.master,w,h,"")
      self.data_box.box.place_forget()
      self.bpm=Label(self.master,text="BPM: ",bg=self.bg_col)
      self.rhythm=Label(self.master,text="Rhythm: ",bg=self.bg_col)
      self.quality=Label(self.master,text="Quality: ",bg=self.bg_col)

      self.place_counter()

   def newData(self,text):
      self.data.config(text=text)


   def place_counter(self):
      self.data.place(relx=0.4,rely=0.3,anchor=CENTER) #relx/relxy are the relative position in the frame (0.5=half the frame)
      self.title.place(relx=0.4,rely=0.47,anchor=CENTER)
   
   def clear_counter(self):
      self.data.place_forget()
      self.title.place_forget()

   def diagnostics(self,info_tuple=None):
      #self.data_box=box(self.master,w,h,"")

      self.bpm_title=Label(self.data_box.fetch(),text="RATE:",bg=self.bg_col)
      self.bpm_title.config(font=(oris.font,25,'bold','underline'))
      self.bpm=Label(self.data_box.fetch(),text="",bg=self.bg_col)
      self.bpm.config(font=(oris.font,25))

      self.rhythm_title=Label(self.data_box.fetch(),text="RHYTHM:",bg=self.bg_col)
      self.rhythm_title.config(font=(oris.font,25,'bold','underline'))
      self.rhythm=Label(self.data_box.fetch(),text="",bg=self.bg_col)
      self.rhythm.config(font=(oris.font,20))

      self.quality_title=Label(self.data_box.fetch(),text="QUALITY:",bg=self.bg_col)
      self.quality_title.config(font=(oris.font,25,'bold','underline'))
      self.quality=Label(self.data_box.fetch(),text="",bg=self.bg_col)
      self.quality.config(font=(oris.font,25))

      #self.place_diag()

   def place_diag(self):
      self.data_box.box.place(relwidth=0.9,relx=0.47,rely=0.38,anchor=CENTER)

      self.bpm_title.place(relx=0.02,rely=0.10,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)
      self.bpm.place(relx=0.02,rely=0.25,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)

      self.rhythm_title.place(relx=0.02,rely=0.40,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)
      self.rhythm.place(relx=0.02,rely=0.55,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)

      self.quality_title.place(relx=0.02,rely=0.75,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)
      self.quality.place(relx=0.02,rely=0.87,anchor=W) #relx/relxy are the relative position in the frame (0.5=half the frame)


   def clear_diag(self):
      self.data_box.box.place_forget()
      
      self.bpm_title.place_forget()
      self.bpm.place_forget()

      self.rhythm_title.place_forget()
      self.rhythm.place_forget()

      self.quality_title.place_forget()
      self.quality.place_forget()

   def set_data(self,data_tuple):
      self.bpm.config(    text=""+str(data_tuple[0]))
      self.rhythm.config( text=""+str(data_tuple[1]))
      self.quality.config(text=""+str(data_tuple[2]))




   def color(self,col):
      self.data.config(bg=col)
      self.title.config(bg=col)



class winlabel():
   def __init__(self,frame,name):
      self.h=30
      self.frame=Frame(frame,height=self.h,width=50)
      self.frame.config(highlightthickness=1,highlightbackground="grey")
      self.frame.pack(fill=X)
      self.label=Label(self.frame,height=self.h,text=name,bg="lightblue")
      self.label.config(font=(oris.font,15))
      self.frame.pack_propagate(False)
      self.label.pack(fill=BOTH)

   def cfg(self,bg,fg):
      self.label.config(bg=bg,fg=fg)
      

# User information
class settings():
   def __init__(self,master):
      self.master=master

      self.label_state="Disabled"
      self.label=Label(self.master,text=self.label_state)
      self.label.config(font=(oris.font,30),bg="white")
      
	
   def toggle(self):
      if(self.label_state=="Disabled"):
          self.label_state="Enabled"
      else:
          self.label_state="Disabled"
      
      self.label.config(text=self.label_state)


   def get_state(self):
      return self.label_state
      
