from tkinter import *
from tkinter import filedialog
import ctypes 
from stix2validator import validate_file, validate_string, print_results,ValidationOptions,validate_instance
from stix2 import Indicator,ThreatActor,AttackPattern,Bundle, Relationship, parse
import json
import random
import math
##create program to open file import jsons- turn to stix objects - combine objects
def add_obj_array(array, file):
    inputString = ""
    with open(file) as f:
        inputString = f.read()
        
        #options = ValidationOptions(strict=True, version="2.2")    
        if( inputString[ 0: 1] == '['):
            jsonList = json.loads(inputString)              
            for jo in jsonList :  
                results = validate_instance(jo)
                if results.is_valid :       
                    obj = parse(jo)
                    if(obj['type'] == 'bundle'):
                        objects = obj['objects']    
                        for o in objects :
                            add_stix_button(o)
                            array.append(o)
                    else:
                        array.append(obj)
                        add_stix_button(obj)
                    print_results(results)
                    print("this is a stix valid json" )
                else:
                    print_results(results)
                    print("this is not a stix valid json")        
        else:
            results = validate_string(inputString)
            if results.is_valid :
                obj = parse(inputString)
                if(obj['type'] == 'bundle'):
                    objects = obj['objects']    
                    for o in objects :
                        array.append(o)
                        add_stix_button(o)
                else:
                    array.append(obj)
                    add_stix_button(obj)
                print_results(results)
                print("this is a stix valid json" )
            else:
                print_results(results)
                print("this is not a stix valid json")

# Function to open a file in the system
def open_file():
   global curInd
   global obj_array
   filepath = filedialog.askopenfilename(title="Open a Text File", filetypes=(("text    files","*.json"), ("all files","*.*")))
   files.append(open(filepath,'r'))
   print(curInd)
   print(files[curInd].name)
   files[curInd].close()   
   nams = "" 
   add_obj_array(obj_array, files[curInd].name)    
   for ele in files:
      nams += ele.name + "\n"
   fileLab.config(text="Files: "+nams)
     
   curInd+=1
   lineUpdate()

def reset(): 
    global files, curInd,obj_array,obj_buttons, sourceObj, targetObj
    files = []
    obj_array = []
    for o in obj_buttons:
        o.destroy()
    obj_buttons = []
    curInd = 0
    fileLab.config(text="Files:")  
    sourceObj = None
    targetObj = None
def createBundle():           
    bundle = Bundle(obj_array)
    ctypes.windll.user32.MessageBoxW(0, "bundle successfully created", "success", 1)
    
    stix_json_string = bundle.serialize(pretty=True)
    print(stix_json_string)
    with open("combine.json", "w") as write_file:
        write_file.write(stix_json_string)

def add_stix_button(stixObj):
    global obj_buttons
    if stixObj.type != 'relationship' :
        stixLab = Label(win, text=stixObj.name,  height= 2, background="gray")
        xloc =  20 + random.randrange(1, 20)*20
        yloc = 150 + random.randrange(1, 20)*20
        stixObj =  StixObject(stixLab, id=stixObj.id, x=xloc, y=yloc, dragable = True)
    else:
        stixLab = Label(win, text=stixObj.relationship_type, height= 2, background="gray")
        xloc =  20 + random.randrange(1, 20)*20
        yloc = 150 + random.randrange(1, 20)*20
        stixObj =  StixObject(stixLab, id=stixObj.id, x=xloc, y=yloc, dragable = False, source = stixObj.source_ref, target = stixObj.target_ref)
    obj_buttons.append(stixObj)

def lineUpdate():
    
    for o in obj_buttons:
        if(o.source != None and o.target != None) :
            if( o.line == None):
                o.makeLine()
            else:
                o.updateLine()

	
#stix obj stuff
def makeReference(sourceId, targetId):
    global obj_array
    print(sourceId, targetId)
    relationship = Relationship(relationship_type='name',                            
        source_ref = sourceId,
        target_ref = targetId,)
    obj_array.append(relationship)
    add_stix_button(relationship)
    lineUpdate()
def find_bottonID( id):
    result = None
    for o in obj_buttons:
        if(o.id == id):
            result = o
    return result

class StixObject():
    widget = None
    target = None
    source = None
    line = None
    id = ""
    def __init__(self, widget, id, x=0, y=0, dragable = True,source = None, target = None):
        self.start_x = 0
        self.start_y = 0
        self.x = x + widget.winfo_reqwidth()/2       
        self.y = y + widget.winfo_reqheight()/2
        self.widget = widget
        self.id = id
        widget.place(x=x, y=y)
        
        if( source != None): 
            self.source = source
        if( target != None):
            self.target = target                

        widget.bind("<ButtonRelease-1>", self.no_click)
        if(dragable):
            widget.bind("<ButtonPress-1>"  , self.drag_Start)
            widget.bind("<B1-Motion>"      , self.drag)
        widget.bind("<Button-1>"       , self.left_click)
        widget.bind("<Button-2>"       , self.right_click)
        widget.bind("<Button-3>"       , self.right_click)
        
    def drag_Start(self, event):
        self.start_x = event.x
        self.start_y = event.y   

    def drag(self, event):       
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        x = event.widget.winfo_x() - event.widget.winfo_reqwidth()/2  + delta_x
        y = event.widget.winfo_y() - event.widget.winfo_reqheight()/2 + delta_y
        self.x = x + event.widget.winfo_reqwidth()/2     
        self.y = y + event.widget.winfo_reqheight()/2
        event.widget.place(x = x, y = y)
        lineUpdate()
        
    def left_click(self,event):              
        event.widget.configure(bg="green")  
        sourceObj = None
        targetObj = None
    def right_click(self, event):
        global sourceObj, targetObj  
        if(self.source == None):      
            if sourceObj == None:
                sourceObj = self.id
                event.widget.configure(bg="red")
            else :
                if(sourceObj != self.id):
                    targetObj =  self.id
                    makeReference(sourceObj, targetObj) 
                    but = find_bottonID(sourceObj)
                    but.widget.configure(bg="gray")  
                    sourceObj = None
                    targetObj = None
                else:
                    event.widget.configure(bg="gray")  
                    sourceObj = None
                    targetObj = None
            
            
    def no_click(self, event):
        event.widget.configure(bg="gray")  
    def destroy(self):
        if( self.line != None):
            canvas.delete(self.line)
        self.widget.destroy()
    def makeLine(self):       
        sbot = find_bottonID(self.source)
        tbot = find_bottonID(self.target)        
        if( sbot != None and tbot != None):            
            self.line = canvas.create_line( sbot.x, sbot.y, tbot.x, tbot.y, tbot.x+6, tbot.y +6)              
            xx = sbot.x + (tbot.x -sbot.x)/2 - self.widget.winfo_reqwidth()/2  
            yy = sbot.y + (tbot.y -sbot.y)/2 - self.widget.winfo_reqheight()/2
            self.widget.place(x=xx, y=yy)
    def updateLine(self):       
        sbot = find_bottonID(self.source)
        tbot = find_bottonID(self.target)        
        if( sbot != None and tbot != None):            
            canvas.coords( self.line, sbot.x, sbot.y, tbot.x, tbot.y)      
            xx = sbot.x + (tbot.x -sbot.x)/2 - self.widget.winfo_reqwidth()/2  
            yy = sbot.y + (tbot.y -sbot.y)/2 - self.widget.winfo_reqheight()/2
            self.widget.place(x=xx, y=yy)                    

# Create an instance of window
win=Tk()
canvas = Canvas(width=800, height=600)
sourceObj = None
targetObj = None
# Set the geometry of the window
win.geometry("800x600")


Label(win, text="Click the button to open a dialog", font='Arial 16 bold').pack(pady=3)


files = []
obj_array   = []
obj_buttons = []

curInd = 0
   
# Create a button to trigger the dialog
button = Button(win, text="Open", command=open_file)
button.pack(pady=5)
fileLab = Label(win, text="Files:", font='Arial 8 bold')
fileLab.place(relx = 0.0, rely = 1.0, anchor ='sw')

resetBut = Button(win, text="Reset", command=reset)
resetBut.pack(pady=5)
makeBut = Button(win, text="MakeBuddle", command=createBundle)
makeBut.pack()

canvas.place(x = 0, y =0)


win.mainloop()