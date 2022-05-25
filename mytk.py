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
        if self.word[ self.pos ].lower() == key.lower():
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
        self.wfinish = {}
        self.pos= 0 #進行状況 何番目のwordか
        
    def loaddata(self, filepath='', **keys ):
        # filepath: ./data.txt (default)
        # keys: count=10, lmin=5, lmax=10, shuffle=True, randomstate=True
        loaddata = mytype(filepath=filepath)
        loaddata.choicewords(**keys)
        self.wlist = loaddata.playwords
        self.wfinish = {}
        self.pos= 0 #進行状況 何番目のwordか

    def getword(self):
        return self.wlist[self.pos]
    def finish(self, playWordData):
        lword = self.getword().lower() 
        if lword not in self.wfinish:
            self.wfinish[lword] = playWordData
        else:
            pass
        self.pos = (self.pos + 1) % len(self.wlist)


class mytk(Tk.Tk):
    def __init__(self, filepath='', **keys ) -> None:
        super().__init__(screenName='mytype')
        self.status = playStatus.wait
        self.playList = playList()
        self.playList.loaddata(filepath, **keys)
        self.playWord = None
        self.ready = 0

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
        self.canvasText = canvasColorText(self.canvas)
        self.canvasText.setfont( tkFont.Font(size=30, weight="bold", \
        # self.canvasText.setfont( tkFont.Font(family="times", size=30, weight="bold", \
            #  slant='italic') );
            ));

        self.canvasText.create_text('Hitkey [Space] or [Enter] to Start!!', 320,140)

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
        

    def onplay(self):
        if self.status == playStatus.ready:
            self.canvasText.create_text(str(self.ready), 320,140)
            self.ready -= 1
            if self.ready >= 0:
                self.after( 1000, self.onplay )
            else:
                self.status = playStatus.play
                self.canvasText.create_text('')

        if self.status == playStatus.play:
            self.playWord = playWord( self.playList.getword() )
            self.canvasText.create_text( self.playWord.word, 320,140 )
            pass
        pass

    def onkeypress(self, key):
        if self.status == playStatus.wait:
            if key.char == '\r' or key.char == ' ': # [Enter] or [space]
                self.status = playStatus.ready
                self.ready = 3
                self.onplay()
        elif self.status == playStatus.ready:
            if key.char == '\x1b': # [esc]
                # 画面リセット
                self.canvasText.create_text('')
                self.status = playStatus.wait
        elif self.status == playStatus.play:
            # print(key)
            if key.char == '\x1b': # [esc]
                pass
            else:
                ret, _ = self.playWord.keycheck(key.char)
                if ret == playStatus.keyok or  ret == playStatus.keymiss:
                    cols = [ 'green' if i < self.playWord.pos else 'blue' for i in range(len(self.playWord.word))]
                    cols[self.playWord.pos] = 'red'
                    self.canvasText.setcolor(cols)
                    pass
                elif ret == playStatus.keyfinish:
                    self.playList.finish(self.playWord)
                    self.onplay()

        elif self.status == playStatus.finish:
            self.status = playStatus.wait


if __name__=='__main__':
    app = mytk()
    app.mainloop()

