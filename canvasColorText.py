#-*- coding: utf-8 -*-
import tkinter as tk
import tkinter.font as tkFont

class canvasColorText():
    def __init__(self, canvas : tk.Canvas, text='', x=0, y=0 ) -> None:
        self.canvas = canvas
        self.font = tkFont.nametofont('TkDefaultFont')
        self.ids = []  # {'id':id,'text':c,'width':m,'height':n}
        self.create_text(text, x, y)
    def create_text(self, text, x=0, y=0):
        self.delete_text()
        if text and len(text):
            for c in text:
                id = self.canvas.create_text( x,y, text=c)
                self.ids.append( {'id':id, 'text':c} )
            self.setfont( self.font)
    def delete_text(self):
        for param in self.ids:
            self.canvas.delete(param['id'])
        self.ids.clear()
    def gettext(self):
        return ''.join( param['text'] for param in self.ids )
    def getpos(self):
        x1,y1,x2,y2 = self.bbox()
        return (x1+x2)//2, (y1+y2)//2
    def bbox(self):
        x1,y1,x2,y2 = 0,0,0,0
        if len(self.ids):
            x1,y1,_,_ = self.canvas.bbox(self.ids[0]['id'])
            _,_,x2,y2 = self.canvas.bbox(self.ids[len(self.ids)-1]['id'])
        return x1,y1,x2,y2
    def moveto(self, x,y):
        x1,y1 = self.getpos()
        self.move(x-x1,y-y1)
    def move(self, x,y):
        for param in self.ids:
            self.canvas.move( param['id'], x, y )
    def setcolor(self, colors ):
        for param, color in zip( self.ids, colors ):
            self.canvas.itemconfigure(param['id'], fill=color )
        if len(colors) < len(self.ids):
            lastColor = colors[ len(colors)-1 ]
            for i in range( len(colors), len(self.ids) ):
                param = self.ids[i]
                self.canvas.itemconfigure(param['id'], fill=lastColor )
    def getfont(self):
        return self.font # tkFont.Font
    def setfont(self, font : tkFont.Font ):
        self.font = font.copy()
        text = self.gettext()
        x0,y0=0,0
        if len(text):
            for i, c, param in zip( range(len(text)), text, self.ids):
                self.canvas.itemconfigure(param['id'], font=self.font)
                self.ids[i]['width'], self.ids[i]['height'] = \
                    self.font.measure(c ), \
                    self.font.metrics("linespace")
                id = self.ids[i]['id']
                xy = self.canvas.coords(id)
                if i==0:
                    x0,y0 =  xy[0], xy[1]
                mx, my = x0 - xy[0], y0 - xy[1]
                self.canvas.move(id, mx, my) #same coordinates of all characters
            x,y = self.getpos()
            self.reposition_canvastext()
            self.moveto(x,y) # coordinates shift of all characters

    def reposition_canvastext(self):
        if len(self.ids):
            xx = - self.ids[0]['width'] / 2;
            for param in self.ids:
                xx += param['width'] / 2;
                self.canvas.move( param['id'], xx, 0 )
                xx += param['width'] / 2;




if __name__=='__main__':
    import math

    class testclass(tk.Tk):
        def __init__(self) -> None:
            super().__init__(screenName='canvastext')
            
            self.canvas = tk.Canvas( self, width=360, height=360)
            self.canvas.pack()

            self.canvasText = canvasColorText(self.canvas)
            # self.canvasText.setcolor(['green'])

            # self.canvasText.create_text('hoge')
            self.canvasText.create_text('[javascript]')
            self.canvasText.setcolor(('red','Yellow','green','blue','red'))
            font = tkFont.Font(family="times", size=30, weight="bold", slant='italic')
            self.canvasText.setfont(font)
            self.mvcounter = 0.05

            # id = self.canvas.create_text(200,50, text='[javascript]')
            # self.canvas.itemconfigure(id, font=font)

        def movetext(self):
            self.canvas['bg'] = 'white'
            cx,cy,r = 180,180,80
            y = cx + r * math.sin( math.radians(self.mvcounter))
            x = cy + r * math.cos( math.radians(self.mvcounter))

            self.canvasText.moveto(x,y)
            # self.after(10, self.movetext)
            self.mvcounter = (self.mvcounter + 1) % 360

    app = testclass()
    app.movetext()
    app.mainloop()

