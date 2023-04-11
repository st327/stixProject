from tkinter import *
from tkinter import filedialog
import tkinter as tk
import ctypes 
from stix2validator import validate_file, validate_string, print_results,ValidationOptions,validate_instance
from stix2 import Indicator,ThreatActor,AttackPattern,Bundle, Relationship, parse
import pyautogui
import json
import random
import math
import string
import keyboard
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
    sourceObj = []
    targetObj = []
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
        stixLab = Label(win, text=stixObj.name +" \n" +stixObj.type,  height= 2, background="gray")
        xloc =  0 + random.randrange(1, 30)*20
        yloc = 150 + random.randrange(1, 30)*20
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

    type = pyautogui.prompt("Relationship type")
    if(type != None):
        if(type == ''):
            type = ''.join(random.choices( string.ascii_lowercase, k=random.randrange(3, 10)))
        relationship = Relationship(relationship_type=type,                            
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
def reference_exists(sourceID, targetId):
    global obj_array
    for o in obj_array:
        if(o.type == 'relationship' and ((o.source_ref == sourceID and o.target_ref == targetId ) 
                                         or (o.source_ref == targetId and o.target_ref == sourceID ) ) ):
            print( "relationship already exist")
            return True
    return False
def createStixObject():      
    options = [   
        "attack-pattern",
     #   "threat-actor",
      #  "indicator",
      #  "malware",
      #  "identity",
        
    ]  
    global menu
    def selectMenu(choice):
        global menu
        menu = variable.get()
        choice = variable.get()
    def clicked():
        global menu
        amount = number.get()
        if(amount == ''):
            amount = 1  
        else:
            amount = int( amount) 
            if(amount > 20 ):
                amount = 20
            if(amount < 0 ):
                amount = 1
        nam = name.get()
      #  description = desc.get()
        for i in range(0, amount):     
            rnam = nam
            if(nam == ''):
                rnam = ''.join(random.choices(string.ascii_uppercase 
                        + string.digits + string.ascii_lowercase, k=random.randrange(3, 10)))
            rmenu = menu
            if(menu == ''):
                rmenu = options[random.randrange(0, len(options))]
            objJson = {
                "name": rnam,
                "type": rmenu,
            }            
    #        if(description != ''):
     #           objJson["Description"] = description
            strJson =  json.dumps(objJson)
            print(strJson)
            obj = parse(strJson)                
            add_stix_button(obj)
            obj_array.append(obj)
                                          
        window.destroy()
                  
    menu = ""
    window = tk.Toplevel()
    window.title("Create Stix object part one")
    window.geometry('300x300')
    window.configure(background = "white")
    variable = StringVar()
    a = Label(window ,text = "Name").grid(row = 0,column = 0)
    b = Label(window ,text = "Type").grid(row = 1,column = 0)
 #   c = Label(window ,text = "Description").grid(row = 2,column = 0)
    d = Label(window ,text = "Number").grid(row = 2,column = 0)    
    name = Entry(window)
    name.grid(row = 0,column = 1)
    type = OptionMenu( window , variable, *options, command=selectMenu )
    type.grid(row = 1,column = 1)
    #desc = Entry(window)
    #desc.grid(row = 2,column = 1)
    number = Entry(window)
    number.grid(row = 2,column = 1)#restrict to ints later
   
    sub = filedialog.Button(window ,text="Submit", command = clicked).grid(row=5,column=0)
    cal = filedialog.Button(window ,text="Cancel", command = window.destroy).grid(row=5,column=1)
    window.mainloop()

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
        global sourceObj, targetObj       
        event.widget.configure(bg="green")  
        sourceObj = []
        targetObj = []
    def right_click(self, event):
        global sourceObj, targetObj  
        if(self.source == None):      
            if sourceObj == [] or keyboard.is_pressed("Shift"):
                sourceObj.append( self.id)
                event.widget.configure(bg="red")
            else :
                if(sourceObj.count( self.id) == 0):
                    for ob in sourceObj:
                        if(not reference_exists(ob, self.id) ):
                            targetObj =  self.id
                            makeReference(ob, targetObj) 
                            but = find_bottonID(ob)
                            but.widget.configure(bg="gray")  
                        else:
                            but = find_bottonID(ob)
                            but.widget.configure(bg="gray")  
                    sourceObj = []
                    targetObj = []
                else:
                    for ob in sourceObj:
                        find_bottonID(ob).widget.configure(bg="gray") 
                    event.widget.configure(bg="gray")  
                    sourceObj = []
                    targetObj = []
            
            
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
            self.line = canvas.create_line( sbot.x, sbot.y, tbot.x, tbot.y, tbot.x, tbot.y-30, tbot.x, tbot.y+30)  
                      
            xx = sbot.x + (tbot.x -sbot.x)/2 - self.widget.winfo_reqwidth()/2  
            yy = sbot.y + (tbot.y -sbot.y)/2 - self.widget.winfo_reqheight()/2
            self.widget.place(x=xx, y=yy)
    def updateLine(self):       
        sbot = find_bottonID(self.source)
        tbot = find_bottonID(self.target)        
        if( sbot != None and tbot != None):            
            canvas.coords( self.line, sbot.x, sbot.y, tbot.x, tbot.y, tbot.x, tbot.y-30, tbot.x, tbot.y+30)      
            xx = sbot.x + (tbot.x -sbot.x)/2 - self.widget.winfo_reqwidth()/2  
            yy = sbot.y + (tbot.y -sbot.y)/2 - self.widget.winfo_reqheight()/2
            self.widget.place(x=xx, y=yy)                    

# Create an instance of window
win=Tk()
canvas = Canvas(width=1000, height=800)
sourceObj = []
targetObj = []
# Set the geometry of the window
win.geometry("900x700")

Label(win, text="Stix bundle maker", font='Arial 16 bold').pack(pady=3)

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
makeBut = Button(win, text="MakeObj", command=createStixObject)
makeBut.pack()
makeBut = Button(win, text="MakeBuddle", command=createBundle)
makeBut.pack()

canvas.place(x = 0, y =0)


win.mainloop()