#coding -*- utf-8 -*-
from dataclasses import dataclass

from sqlalchemy import false, true
import numpy as np
import re
import msvcrt
import time
import sys
# import gc

import winsound

class wordlog:
    def __init__(self) -> None:
        pass
    def start(self, word:str):
        self.keyinstart = time.time()
        self.word = word.lower()
        self.misscnt = 0
        wordchr = set( i for i in self.word )
        self.misschr = { i:0 for i in wordchr }
        self.pos = -1
        pass
    def end(self):
        self.keyinend   = time.time()
        #print ( '--> {}: {:.2f}, miss={}\n'.format(self.word, self.keyinend - self.keyinstart, self.misscnt) )
        pass

    def keyin(self, i, miss):
        if miss:
            if self.pos != i:
                self.misscnt += 1 #積上げ
                chr = str(self.word[i]).lower()
                self.misschr[chr] += 1 #積上げ
                self.pos = i
        pass

@dataclass
class dataw:
    word    : str = ''
    count   : int = 0 # word 回数
    miss    : int = 0 # miss 回数
    missper : float = 0. # miss率
    pass

class playlog:
    def __init__(self) -> None:
        pass
    def start(self):
        self.playstart = time.time()
        self.playend = 0
        self.wordtime = 0 #総入力時間
        self.totalcnt_words = 0 #word 総数
        self.totalcnt_chrs = 0 #char 総数
        self.misscnt_words = 0  #word miss総数
        self.misscnt_chrs = 0  #char miss総数
        self.worddata = dict() #word データ {<word>:dataw}
        self.misschrs  = dict() #char データ {<char>:miss_count}

    def end(self):
        self.playend = time.time()
        pass
    def addword(self, wordlog: wordlog):
        if wordlog.word not in self.worddata:
            self.worddata[wordlog.word] = dataw()

        #この単語で miss した文字
        #misschr =  dict( filter( lambda item: item[1] > 0, wordlog.misschr.items() ) ) #miss したchrのみ
        misschr_cnt = 0 #miss した文字数
        for val in wordlog.misschr.values():
            misschr_cnt += val

        self.totalcnt_words += 1 #word 総数
        if wordlog.misscnt > 0: #word miss総数
            self.misscnt_words += 1
        self.wordtime += wordlog.keyinend - wordlog.keyinstart #総入力時間
        self.totalcnt_chrs += len( wordlog.word )#char 総数
        self.misscnt_chrs += misschr_cnt #char miss総数

        # worddata  {<word>:dataw}
        self.worddata[ wordlog.word ].word = wordlog.word
        self.worddata[ wordlog.word ].count+= 1
        self.worddata[ wordlog.word ].miss += misschr_cnt
        self.worddata[ wordlog.word ].missper = self.worddata[ wordlog.word ].miss * 100.  \
                                            / ( self.worddata[ wordlog.word ].count * len(wordlog.word) )

        #misschrs {<char>:miss_count}
        for ch, val in wordlog.misschr.items():
            if ch not in self.misschrs:
                self.misschrs[ch] = 0
            self.misschrs[ch] += val
        pass
    def console_result(self):
        if self.totalcnt_words > 0:

            playtime = self.playend - self.playstart
            inpspeed = 1.0 / (self.wordtime / self.totalcnt_chrs ) #1sec あたりの 入力速度 net
            misschrs = sorted( self.misschrs.items(), key=lambda x:x[1], reverse=True )

            print('\n<< score >>')
            print('input-word: {}, success: {} ({:.2f} %), miss: {}'.format( 
                self.totalcnt_words,
                self.totalcnt_words-self.misscnt_words,
                (self.totalcnt_words-self.misscnt_words)*100.0 / self.totalcnt_words,
                 self.misscnt_words ))
            print('input-chr: {}, success: {} ({:.2f} %), miss: {}'.format( 
                self.totalcnt_chrs,
                self.totalcnt_chrs-self.misscnt_chrs,
                (self.totalcnt_chrs-self.misscnt_chrs)*100.0 / self.totalcnt_chrs,
                 self.misscnt_chrs ))

            print('play-time: {:.2f} (sec)'.format(playtime) )
            print('input-time: {:.2f}, ({:.2f} %)'.format(self.wordtime, self.wordtime * 100. / playtime  ))
            print('input-speed: {:.2f} (chr/sec)'.format(inpspeed) )
            #print('input-speed-net: {:.3f} (sec/chr)'.format(keyinspeed_in_chr) )

            print('miss char: ', end='')
            for i, (c,v) in enumerate(misschrs):
                if i > 10 or v == 0:
                    break
                print( '({}:{}), '.format(c,v), end='' )
            print('\n')
        pass

class mytype():

    def __init__(self, filepath='') -> None:
        if len(filepath) == 0:
            filepath = './data.txt'
        self.originalwords = mytype.loaddata( filepath )
        self.playwords = []
        self.playmode = 0
        self.misswords = []
        self.choice_param = dict()

        self.playlog = playlog()
        self.wordlog    = wordlog()

    @staticmethod
    def loaddata(filepath):
        if filepath=='':
            filepath = './data.txt'
        words = set()
        lwords = []
        with open(filepath, mode='rt') as f:
            while True:
                fl =  f.readline()
                if fl == '':
                    break
                l = re.split('[|{}./;:{}(),= \'/\\"\[\]<>!#0123456789]', fl.rstrip() )
                for i in l:
                    if i != '':
                        words.add(i)
        lwords = list( words)
        # lwords = np.array(lwords)
        return lwords

    def choicewords(self, **keys):
        """ \\
        Examples: \\
        newwords = choicewords( words, count=10, lmin=5, lmax=10, \\
            shuffle=True, randomstate=True) 
        """
        self.playwords = []
        lwords = np.array(self.originalwords)
        count = lwords.shape[0]
        lmin = 1
        lmax = -1
        shuffle = False
        randomstate = 0
        if True:
            if 'count' in keys:
                count = keys['count']
            if 'lmin' in keys:
                lmin = keys['lmin']
            if 'lmax' in keys:
                lmax = keys['lmax']
            if 'shuffle' in keys:
                shuffle = keys['shuffle']
            if 'randomstate' in keys:
                randomstate = keys['randomstate']
        # save param
        self.choice_param['count'] = count
        self.choice_param['lmin'] = lmin
        self.choice_param['lmax'] = lmax
        self.choice_param['shuffle'] = shuffle
        self.choice_param['randomstate'] = randomstate

        lenwords = np.zeros(lwords.shape[0], dtype=np.int)
        for i, word in enumerate(lwords):
            lenwords[i] = len(word)

        lenfilt = np.array([ True for i in range(lwords.shape[0]) ])
        if lmin > 1:
            lenfilt = lenfilt * np.where( lenwords >= lmin, True, False )
        if lmax > lmin:
            lenfilt = lenfilt * np.where( lenwords <= lmax, True, False )
        lwords = lwords[lenfilt]

        if shuffle:
            if randomstate != 0:
                # lwords = np.delete( lwords, np.s_[count::] )
                np.random.seed(randomstate)
            np.random.shuffle(lwords)
        lwords = np.delete( lwords, np.s_[count::] )

        if lwords.shape[0] > 0:
            self.playwords = lwords
        return self.playwords.shape[0]

    def keyin(self, status, word, i=0, key='', miss=0):
        #start word
        if status == 0:
            self.wordlog.start(word)
            #console out
            if self.playmode==1:
                print('\n_ ' + word)
        #key input
        elif status == 1:
            self.wordlog.keyin(i, miss)
            #console out
            if self.playmode==1:
                offset = 0
                misstext = ''
                if not miss:
                    offset = 1
                    winsound.Beep(500,100) #262,294,330,349,392,440,494,532
                else:
                    winsound.Beep(1000,100) #262,294,330,349,392,440,494,532
                    misstext = '    !!miss'

                if i+1 < len(word):
                    print(word[:i + offset]+'_', word[i+ offset:], misstext )

        #end word
        elif status==2:
            self.wordlog.end()
            pass

    def shufflenext(self):
        self.choicewords(
            count=self.choice_param['count'],
            lmin=self.choice_param['lmin'],
            lmax=self.choice_param['lmax'],
            shuffle=self.choice_param['shuffle'],
            randomstate=self.choice_param['randomstate'])

    def console_play(self, endless=False, perfectmode=False):
        print('--- Lets have fun typing!: endress:{}, perfect:{} ---'.format(endless, perfectmode) )
        self.playmode = 1
        self.playlog.start()

        abort = 0
        loopcnt = 0
        while abort==0:
            loopcnt += 1

          # 候補単語ー２順目以降
            if len(self.misswords) > 0:

                #１巡目終了時のみレポート表示
                if loopcnt == 2:
                    print('\n--- 1 巡目の結果 ---')
                    self.playlog.end()
                    self.playlog.console_result()
                    if not self.console_ready(countdown=False):
                        break

            # 前回入力ミスした単語で実施
                self.playwords = np.array( self.misswords )
                self.misswords = [] # ミス単語保存用 クリア
            elif loopcnt > 1:
            # 入力ミスがなければ、候補を選びなおす。
                self.shufflenext()

            print('\n--- {} 巡目-単語数: {} ---'.format(loopcnt, len(self.playwords) ))

            # タイピング
            for word in self.playwords:
                # 単語の開始
                self.keyin(0, word)
                misscnt = 0
                while true: #単語入力ループ
                    perfect_miss = 0
                    for i, c in enumerate(word):
                        while abort==0:
                            key = msvcrt.getch().decode(encoding='ansi')
                            msvcrt.getch() #0x00

                            if str(key).lower() == str(c).lower():
                                self.keyin(1, word, i, key, 0)
                                break
                            if  key == '\x1b':   #ESC
                                abort=1

                            self.keyin( 1, word, i, key, 1) #miss
                            misscnt += 1
                            perfect_miss = 1
                            if perfectmode: #perfectmodeでミスしたらはじめから
                                print('\n_ {}    ***start over***'.format(word))
                                break
                        if abort:
                            break
                        if perfectmode and perfect_miss: #perfectmodeでミスしたらはじめから
                            break
                        # 単語入力終了

                    if abort: # 途中終了なら単語入力ループから抜ける
                        break
                    if not perfectmode: # perfectmode でなければ単語入力ループから抜ける
                        break
                    if perfect_miss==0: # １単語入力中にミスがなければ単語入力ループから抜ける
                        break
                if abort:
                    break
                self.keyin(2, word)
                self.playlog.addword( self.wordlog )
                if misscnt:
                    self.misswords.append(word) # ミス単語保存

            if not endless:
                break;

        self.playlog.end()
        self.playmode = 0

    @staticmethod
    def console_ready(console = true, countdown=True):
        print('--- Hit anykey to start! (cancel: [ESC]) ---')
        key = msvcrt.getch().decode(encoding='ansi')
        msvcrt.getch() #0x00
        if  key == '\x1b':   #ESC
            return False
        if not countdown:
            return True
        
        print('ready...\n3')
        winsound.Beep(800,500)
        time.sleep(0.5)
        print('2')
        winsound.Beep(800,500)
        time.sleep(0.5)
        print('1')
        winsound.Beep(800,500)
        time.sleep(0.5)
        print('-----  ', end='')
        winsound.Beep(1200,1000)
        print('Go!!')
        return True

if __name__=='__main__':
    for argc in sys.argv:
        pass

    typing = mytype (filepath='')
    print( 'typing words:',len(typing.originalwords) )

    count = typing.choicewords(lmin=2, lmax=99, count=100)
    print( 'typing words:', count )

    #print( typing.playwords )

    if typing.console_ready():
        typing.console_play(endless=True, perfectmode=True)
        typing.playlog.console_result()

