from tkinter import *
from tkinter import filedialog
import ctypes 
from stix2validator import validate_file, validate_string, print_results,ValidationOptions,validate_instance
from stix2 import Indicator,ThreatActor,AttackPattern,Bundle, Relationship, parse
import json

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
                            array.append(o)
                    else:
                        array.append(obj)
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
                else:
                    array.append(obj)
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
def reset(): 
    global files, curInd,obj_array
    files = []
    obj_array = []
    curInd = 0
    fileLab.config(text="Files:")  
def createBundle():
           

    bundle = Bundle(obj_array)
    ctypes.windll.user32.MessageBoxW(0, "bundle successfully created", "success", 1)
    
    stix_json_string = bundle.serialize(pretty=True)
    print(stix_json_string)
    with open("combine.json", "w") as write_file:
        write_file.write(stix_json_string)
#stix obj stuff
def drag(event):
    print( event.x, event.y) 
 #   event.widget.configure(bg="green")
def left_click(event):
    event.widget.configure(bg="green")

def right_click(event):
    event.widget.configure(bg="red")
    
def no_click(event):
    event.widget.configure(bg="gray")
# Create an instance of window
win=Tk()

# Set the geometry of the window
win.geometry("700x500")


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

stixObj = Label(win, text="placeHolder", width=10, height= 2, background="gray")
stixObj.place(x=20, y=150)

stixObj.bind("<Motion>", drag)
stixObj.bind("<Button-1>", left_click)
stixObj.bind("<Button-2>", right_click)
stixObj.bind("<Button-3>", right_click)
stixObj.bind("<ButtonRelease-1>", no_click)


win.mainloop()