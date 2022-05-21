#-*- coding:utf-8 -*-

from dataclasses import dataclass
import tkinter as Tk
import tkinter.font as tkFont
import numpy as np
from enum import Enum

from mytype import mytype
from canvasColorText import canvasColorText

# @dataclass
# class playStatus():
class playStatus(Enum):
    # use mytk
    wait  = 0
    ready = 1
    play  = 2
    finish= 0
    # use playWord
    keymiss  = 0
    keyok    = 1
    keyfinish= 2

class playWord():
    def __init__(self, word) -> None:
        self.word  = word
        self.pos = 0 #進行状況 何番目の文字か
        self.miss  = [ 0 for _ in range( len(self.word) ) ]
       
    def keycheck(self, key):
        # return status, pos
        if self.word[ self.pos ] == key:
            self.pos += 1
            if self.pos < len(self.word):
                return playStatus.keyok, self.pos
            return playStatus.keyfinish, -1
        else:
            self.miss[self.pos] = 1
            return playStatus.keymiss, self.pos

class playList():
    
    def __init__(self) -> None:
        self.wlist  = []
        self.finish = {}
        self.pos= 0 #進行状況 何番目のwordか
        
    def loaddata(self, filepath='', **keys ):
        # filepath: ./data.txt (default)
        # keys: count=10, lmin=5, lmax=10, shuffle=True, randomstate=True
        loaddata = mytype(filepath=filepath)
        loaddata.choicewords(**keys)
        self.wlist = loaddata.playwords
        self.finish = {}
        self.pos= 0 #進行状況 何番目のwordか

    def getword(self):
        return self.wlist[self.pos]
    def finish(self, playword):
        lword = self.getword().lower() 
        if lword not in self.wlist:
            self.finish[lword] = playword
        else:
            pass
        self.pos = (self.pos + 1) % len(self.wlist)


class mytk(Tk.Tk):
    def __init__(self, filepath='', **keys ) -> None:
        super().__init__(screenName='mytype')
        self.status = playStatus.wait
        self.playList = playList()
        self.playList.loaddata(filepath, **keys)

        # self.geometry('640x480')
        self.protocol('WM_DELETE_WINDOW', self.onclose)
        # self.grid()
        self.header = Tk.Canvas(self, width=640, height=100)
        self.canvas = Tk.Canvas(self, width=640, height=280)
        self.footer = Tk.Canvas(self, width=640, height=100)
        
        self.header.grid(column=0, row=0)
        self.canvas.grid(column=0, row=1)
        self.footer.grid(column=0, row=2)

        # word = self.playList.getword()
        # word = self.playList.getword()
        text = 'abcdef'
        text = [ i for i in text ]
        ids = {}
        for c in text:
            id = self.canvas.create_text(100, 20, text=c);
            x1,y1, x2,y2 = self.canvas.bbox(id)
            ids[id] = (x2-x1+1,y2-y1+1)

        x = 100
        y = 50
        for id, (w,h) in ids.items():
            self.canvas.move( id, x , y )
            self.canvas.itemconfigure(id, fill='red')
            x += w

        # fontname = self.canvas.itemcget(ids[0], 'font')
        # font = tkFont.nametofont(fontname)
        # size = font["size"]
        # self.canvas.itemconfigure(ids[0],font=font)
        # self.canvas.move()


        self.canvas.bind('<KeyPress>', self.onkeypress)
        self.canvas.focus_set()


    def onclose(self):
        self.destroy()

    def maniloop(self):
        super().mainloop()
        

    def ondraw(self):
        pass
    def onkeypress(self, key):
        print(key)
        if key.char == '\x1b': # [esc]
            pass
        if key.char == '\r' or key.char == ' ': # [Enter] or [space]
            pass


if __name__=='__main__':
    app = mytk()
    app.mainloop()

