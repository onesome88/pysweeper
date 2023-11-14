"""
# EXTREMELY UNSTABLE CODE
DO NOT:
- Make RenderX or RenderY odd values.
- Make board_x equal to or smaller than RenderX.
- Make board_y equal to or smaller than RenderY.
Otherwise it works somewhat well.
"""
import tkinter as tk
import random
import keyboard
from CTkMenuBar import *

MAX_BOARD_SIZE = 5000
BOARD_TOO_BIG_ERROR = f"You cannot have board sizes passing {MAX_BOARD_SIZE}. It's just stupid."
TOO_MANY_MINES_ERROR = "More mines specified than board cells! \n consider decreasing mine_count or increading board size."
SURROUNDINGS = [[0,1],[1,0],[1,1],[-1,0],[0,-1],[-1,1],[1,-1],[-1,-1]]
COLORS = ["#000000",
          "#0000ff",
          "#00ff00",
          "#99ff00",
          "#ffff00",
          "#ff9900",
          "#ff0000",
          "#990000",
          "#9900ff"]

class Set(): #embedded custom Set library
    def __init__(self,items:list):
        self.set = items
    def append(self,value):
        if value in self.set:
            raise ValueError(f"\"{value}\" Already exists in set")
        else:
            self.set.append(value)
    def index(self,value):
        return self.set.index(value)
    def exists(self,value):
        if value not in self.set:
            raise ValueError(f"{value} doesn't exist in {self.set}")
        else:
            return True
    def len(self):
        return len(self.set)
    def __str__(self):
        return str(self.set)
    def update(self):
        self.set2 = self.set.copy()
        self.set = []
        for value in self.set2:
            self.append(value)
        self.set = self.set2.copy()

flags = Set([])
blocks_opened = Set([])
mines = []
board_x = 10 #board width
board_y = 10 #board height
mine_count = round(board_x*board_y/(100/8))-2 #<- automatic mine calculation
font_size = 15
cell_width = 3
cell_height = 1
left = board_x*board_y
flagMode = False #True to flag stuff, False to not
isFirstClick = True
time = 0
timerStepSize = 10
timerStopped = True
cameraX = board_x/2
cameraY = board_y/2
renderX = 10
renderY = 10

row = []
blocks_copy = []

for idk in range(board_x):
    row.append(None)
for idk2 in range(board_y):
    blocks_copy.append(row)

blocks = blocks_copy.copy()

main = tk.Tk()

frm_game = tk.Frame(master=main,bd=8,relief="ridge")

def calledOnMouseWheel(event):
    if keyboard.is_pressed("Shift"):
        scl_scrollX.set(scl_scrollX.get()-event.delta/120)
    else:
        scl_scrollY.set(scl_scrollY.get()-event.delta/120)

def updateScroll(whatever=None):
    global cameraX,cameraY
    cameraX = scl_scrollX.get()
    cameraY = scl_scrollY.get()
    for y in range(board_y):
        for x in range(board_x):
            blocks[y][x].updateGrid()

def inrange(a,b,dist):
    return True if abs(a-b)<dist/2 else False

def addTimer():
    if not timerStopped:
        global time
        time += 1/timerStepSize
        main.after(round(1000/timerStepSize),addTimer)
        lbl_time.configure(text=f"Time: {round(time,3)}")

def refreshBoardforFirstClick(refreshed_x,refreshed_y):
    """
    ## {function does not work properly}
    Called on user's first click if they clicked on a mine.
    - Finds a new spot to place the mine (openSpace)
    - Clears the clicked cell (refreshed_x, refreshed_y)
    - Applies mine to the found cell (openSpace)
    
    try it by setting board_x=10, board_y=10 & mine_count=99
    if you got any ideas on how to fix, please lmk
    """
    global isFirstClick
    for y in range(board_y):
        for x in range(board_x):
            if not blocks[y][x].isMine:
                openSpace = [x,y] #find some open space
                #print(openSpace)
                break
        try:
            openSpace
        except:
            pass
        else:
            break
    blocks[refreshed_y][refreshed_x].unMineIt() #un-mine the clicked spot
    blocks[openSpace[0]][openSpace[1]].mineIt() #mine the chosen empty spot, doesn't seem to work
    
    for y in range(board_y):
        for x in range(board_x):
            blocks[y][x].doMineCheck()
            #blocks[y][x].updateText()
    
    isFirstClick = False
    
    blocks[openSpace[0]][openSpace[1]].open()

def lrange(a:int,b:int): #range() but returns a list
    l = []
    for i in range(a,b):
        l.append(i)
    return l

def toggle(value):
    return value!=True #just returns the opposite of inputted value

def calledOnKeyPress(event):
    global cameraX,cameraY
    match event.char:
        case "f":
            toggleFlag()
        case "r":
            restartBoard()
        case "w":
            scl_scrollY.set(scl_scrollY.get()-1)
        case "s":
            scl_scrollY.set(scl_scrollY.get()+1)
        case "a":
            scl_scrollX.set(scl_scrollX.get()-1)
        case "d":
            scl_scrollX.set(scl_scrollX.get()+1)
    return updateScroll()

def toggleFlag(event=None):
    global flagMode
    flagMode = toggle(flagMode)
    btn_flag.configure(text=f"Flag: {flagMode}")

def win():
    global timerStopped
    timerStopped = True
    for row in blocks:
        for block in row:
            if block.isMine:
                block.btn.configure(bg="#ff9999",text="X",state="disabled")
            else:
                block.btn.configure(bg="#99ff99")

    lbl_minesRemaining.configure(text="You Won!",bg="#00ff00")

def updateLeft():
    global left
    left = board_x*board_y-blocks_opened.len()
    lbl_minesRemaining.configure(text=f"Left: {left}")

def ranX():
    return random.randint(0,board_x-1)
def ranY():
    return random.randint(0,board_y-1)

def lose():
    global timerStopped
    timerStopped = True
    for y in range(board_y):
        for x in range(board_x):
            blocks[y][x].openRevealLess()
    lbl_minesRemaining.config(text="You Lost",fg="#ffffff",bg="#ff0000")

class Block():
    def __init__(self,x:int,y:int,isMine:bool=False):
        self.x = x
        self.y = y
        self.isMine = isMine
        self.isFlagged = False
        self.isOpened = False
        self.text = None
        blocks[self.y][self.x] = self

        self.btn = tk.Button(master=frm_game,text="",command=self.open,width=cell_width,height=cell_height,font=("Arial",font_size,"bold"),bd=5)
    def open(self):
        global isFirstClick,timerStopped
        if isFirstClick:
            isFirstClick = False
            timerStopped = False
            main.after(0,addTimer)
            if self.isMine:
                refreshBoardforFirstClick(self.x,self.y)
                self.isMine = False
        if not flagMode:
            if not self.isFlagged:
                self.isOpened = True
                self.btn.configure(text=self.text,bg="#999999")
                try:
                    blocks_opened.append([self.y,self.x])
                except:
                    pass
                updateLeft()
                if self.isMine:
                    self.btn.configure(text="X",bg="#ff0000")
                    lose()
                    return
                if self.count==0:
                    for coord in SURROUNDINGS:
                        if self.y+coord[1] < 0:
                            #print("continuing because self.y+coord[1] < 0")
                            continue
                        if self.x+coord[0] < 0:
                            #print("continuing because self.x+coord[0] < 0")
                            continue
                        if self.y+coord[1] > board_y-1:
                            #print("continuing because self.y+coord[1] > 9")
                            continue
                        if self.x+coord[0] > board_x-1:
                            #print("continuing because self.x+coord[0] > 9")
                            continue
                        try:
                            blocks_opened.exists([self.y+coord[1],self.x+coord[0]])
                        except:
                            #print("blocks_opened.exists() threw an error")
                            pass
                        else:
                            #print("blocks_opened.exists() ran successfully")
                            continue
                        blocks_opened.append([self.y+coord[1],self.x+coord[0]])
                        blocks[self.y+coord[1]][self.x+coord[0]].open()
                        blocks_opened.update()
                #print(blocks_opened,end="\n\n")
                if left <= mine_count:
                    win()
        elif not self.isOpened:
            self.isFlagged = toggle(self.isFlagged)
            if self.isFlagged:
                self.btn.configure(text="?",fg="#ff9900")
            else:
                self.btn.configure(text="",fg=COLORS[self.count])
    def updateGrid(self):
        if inrange(self.x,cameraX,renderX) and inrange(self.y,cameraY,renderY):
            self.btn.grid(row=round(self.y-(cameraY-(renderY/2))),column=round(self.x-(cameraX-(renderX/2))),sticky="news")
        else:
            self.btn.grid_remove()
    def openRevealLess(self):
        if self.isMine:
            self.btn.configure(text="X" if not self.isFlagged else "?!",bg="#ff0000",state="normal")
        else:
            self.btn.configure(bg="#ff9999",state="disabled")
        if self.isFlagged and not self.isMine:
            self.btn.configure(text="!!")
    def doMineCheck(self):
        self.count = 0
        for coord in SURROUNDINGS:
            if self.y+coord[1] < 0:
                continue
            if self.x+coord[0] < 0:
                continue
            try:
                if blocks[self.y+coord[1]][self.x+coord[0]].isMine:
                    self.count = self.count + 1
            except:
                pass
        self.btn.configure(fg=COLORS[self.count] if not self.isMine else "#ffffff")
        self.text = self.count if self.count>0 else "" if not self.isMine else "X"
        #print(f"Checked: {self.count}")
    def mineIt(self):
        self.isMine = True #still doesn't work :(
        self.doMineCheck()
    def unMineIt(self):
        self.isMine = False 
        self.doMineCheck()

def restartBoard():
    global blocks,mines,blocks_opened,blocks_copy,row,mine_count,isFirstClick,timerStopped,time,cameraX,cameraY
    time = 0
    timerStopped = True
    isFirstClick = True
    scl_scrollX.set(renderX/2-1)
    scl_scrollY.set(renderY/2-1)
    mine_count = abs(mine_count)
    lbl_minesRemaining.config(text=f"Left: {board_x*board_y}",bg="#F0F0F0",fg="#000000")
    lbl_time.config(text="Time: 0")
    blocks_opened = Set([])
    mines = []
    row = []
    blocks_copy = []

    for _ in range(board_x):
        row.append(None)

    for _ in range(board_y):
        blocks_copy.append(row.copy())

    blocks = blocks_copy.copy()
    
    if mine_count > board_x*board_y:
        raise OverflowError(TOO_MANY_MINES_ERROR)
    if board_x*board_y > MAX_BOARD_SIZE:
        raise OverflowError(BOARD_TOO_BIG_ERROR)
    
    for _ in range(mine_count): #Mine placement
        ran_x = ranX()
        ran_y = ranY()
        try:
            mines.index([ran_x,ran_y]) #Check if slot is already a mine
        except:
            isMine = False
        else:
            isMine = True #If it's already a mine, Start a loop to try again
            while isMine:
                ran_x = ranX()
                ran_y = ranY() #Loop randomizes coordinates again
                try:
                    mines.index([ran_x,ran_y]) #Checks to see if the new coords are a mine
                except:
                    isMine = False #If not, coords are chosen, stop loop
                else:
                    isMine = True #If yes, continue loop
        mines.append([ran_x,ran_y])

    for y in range(board_y):
        for x in range(board_x):
            try:
                mines.index([x,y])
            except:
                Block(x,y,False)
            else:
                Block(x,y,True)

    for y in range(board_y):
        for x in range(board_x):
            blocks[y][x].doMineCheck()
    updateScroll()

frm_options = tk.Frame(master=main)

lbl_minesRemaining = tk.Label(master=frm_options,text=f"Left: {board_x*board_y}",relief="raised",bd=5,width=8,height=1,font=("Arial",18,"bold"))
lbl_minesRemaining.grid(row=0,column=2,columnspan=2,sticky="news")

lbl_mines = tk.Label(master=frm_options,text=f"Mines: {mine_count}",relief="raised",bd=5,width=8,height=1,font=("Arial",18,"bold"))
lbl_mines.grid(row=0,column=4,columnspan=2,sticky="news")

btn_flag = tk.Button(
    master=frm_options,
    text=f"Flag: {flagMode}",
    relief="raised",bd=5,
    width=8,height=1,
    font=("Arial",18,"bold"),
    command=toggleFlag
    )
btn_flag.grid(row=0,column=6,columnspan=2)

btn_optionsMenu = tk.Button(
    master=frm_options,text="Options..",
    command=lambda: btn_optionsMenu.config(text="ERROR"),
    width=8,height=1,
    bd=5,
    font=("Arial",18,"bold"))
btn_optionsMenu.grid(row=0,column=8,columnspan=2)

lbl_time = tk.Label(master=frm_options,text="Time: 0",bd=5,font=("Arial",18,"bold"),width=8,height=1,relief="raised")
lbl_time.grid(row=0,column=10,columnspan=2,sticky="news")

frm_options.pack()
frm_options.rowconfigure(lrange(0,board_y),weight=1)
frm_options.columnconfigure(lrange(0,board_x),weight=1)

scl_scrollX = tk.Scale(
    master=frm_game,
    command=updateScroll,
    orient="horizontal",
    showvalue=False,
    sliderlength=(renderX*50)/board_x*2,
    length=renderX*50,
    from_=renderX/2+1,
    to=board_x-renderX/2-1
)
scl_scrollX.grid(row=board_x+1,column=0,columnspan=board_x)
scl_scrollY = tk.Scale(
    master=frm_game,
    command=updateScroll,
    orient="vertical",
    showvalue=False,
    sliderlength=(renderY*50)/board_y*2,
    length=renderY*50,
    from_=renderY/2+1,
    to=board_y-renderY/2-1
)
scl_scrollY.grid(column=board_y+1,row=0,rowspan=board_y)

frm_game.pack()
frm_game.rowconfigure(lrange(0,renderY+1),weight=1)
frm_game.columnconfigure(lrange(0,renderX+1),weight=1)

men_main = tk.Menu(master=main)

men_options = tk.Menu(master=men_main,tearoff=False)
men_options.add_command(label="New..",command=None)
men_options.add_command(label="Restart",command=restartBoard)

men_main.add_cascade(label="Board",menu=men_options)

restartBoard()

main.title("PySweeper")
main.bind("<KeyPress>",calledOnKeyPress)
main.bind("<MouseWheel>",calledOnMouseWheel)
#main.after(1000,addTimer)
main.rowconfigure([0,1],weight=1)
main.configure(menu=men_main)
main.mainloop()