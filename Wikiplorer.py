# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 11:16:53 2014

@author: manjai

"""
# Wikiplorer : Wikipedia browsing with hyperlink graph 
# PyQt and Webkit for browser and user interface
#
#-------------------------------------------------------------------
# This file may be used under the terms of the GNU General Public
# License versions 2.0 or 3.0 as published by the Free Software
# Foundation and appearing in the files LICENSE.GPL2 and LICENSE.GPL3
# included in the packaging of this file.  Alternatively you may (at
# your option) use any later version of the GNU General Public
# License if such license has been publicly approved by Riverbank
# Computing Limited (or its successors, if any) and the KDE Free Qt
# Foundation. In addition, as a special exception, Riverbank gives you
# certain additional rights. These rights are described in the Riverbank
# GPL Exception version 1.1, which can be found in the file
# GPL_EXCEPTION.txt in this package.
# 
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#--------------------------------------------------------------------------


import signal
import sys

from random import *
from math import fabs, sqrt
from operator import itemgetter
import textwrap

from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

DENSITY = 15000         # square pixel per node  
KF = 110                # F-R distance
MAXEDGE = 6  
LENGTH = 18

flag_self = True
flag_click = False
flag_rclick = False
flag_quit = False
mx = 0                  # dummy for global
my = 0
nnodes = 10             # temporary number for global variables
nedges = 10 
maxnodes = 10
maxedges = 10

x = list()
y = list()
r = list()
wt = list()

olinktable = []
allnodes = []
wordlist = []

dic_olink = dict()
dic_type = dict()
dic_redirect = dict()
dic_nodes = dict()      # nodes for each session 

nodes = []
edges = []
cnodes = []

ncolor = ('#e08080','#e080e0','#a0a0e0','#60e060','#60e0e0','#e0e060', \
        '#d0d0d0')
dic_num = {'인명': 0, '단체': 1, '사건': 2, '지명': 3, '사물': 4, '개념': 5, \
           '기타': 6 }            

LINKPATH = 'wlink.txt'
TYPEPATH = 'wtype.txt'
REDIRECTPATH = 'redirect.txt'


"""
    read all information and put to dictionary or tables
"""
def read_files():
    
    folink = open(LINKPATH, 'r', encoding ='utf-8')
    ftype  = open(TYPEPATH, 'r', encoding ='utf-8')
    fredir = open(REDIRECTPATH, 'r', encoding ='utf-8')
        
    k = 0
    for line in folink:
        links = []
        line = line[:-1]           # remove newline
        tokens = line.split('|')
        if len(tokens) <=1 : continue
        src = tokens[0]
        for i in range(1, len(tokens)):
            dst = tokens[i]
            link = (src,dst)
            links.append(link)
        dic_olink[src] = k
        olinktable.append(links)
        allnodes.append(src)        # for random node generation
        k += 1        
    folink.close()
    print ('link table count = ', k)
       
    k=0
    for line in ftype:
        line = line[:-1]           # remove newline
        tokens = line.split('|')
        if len(tokens) <=1 : info = '기타'
        word = tokens[0]
        info = tokens[1]
        dic_type[word] = info
        k += 1
    ftype.close()
    print('type inormation count = ', k)
  
    k=0
    for line in fredir:
        line = line[:-1]           # remove newline
        tokens = line.split('|')
        if len(tokens) <=1 : info = '기타'
        word = tokens[0]
        info = tokens[1]
        dic_redirect[word] = info
        k += 1
    ftype.close()
    print('redirect inormation count = ', k)  
    
"""
    from wordlist to tnodes 
    return : number of tnodes and tedges as global 
"""
def word_to_nodes():
    global nnodes, nedges, nodes, edges
    
    cannodes = []
    tnodes = []
    tedges = []

    for word in wordlist:
        if flag_self: cannodes.append(word)
        if word in dic_olink:
            idx = dic_olink[word]
            links = olinktable[idx]
            for link in links:
                dst = link[1]
                if dst not in cannodes :
                    if dst not in wordlist:
                        cannodes.append(dst)
    nnodes = len(cannodes)
                        
    # finished candidate nodes now check validity
    for node in cannodes:
        if node not in dic_olink: continue
        idx = dic_olink[node]
        links = olinktable[idx]
        for link in links:
            src = link[0]
            dst = link[1]
            if src != dst :
                link2 = (dst,src)           # 검색어 제외 시 문제 제기함 
                if dst in cannodes:
                    # bidirectional link handling
                    if link not in tedges and link2 not in tedges:
                        tedges.append(link)
                    if dst not in tnodes:
                        tnodes.append(dst)
                    if src not in tnodes:
                        tnodes.append(src)
    nodes = tnodes.copy()
    edges = tedges.copy()
    nnodes = len(tnodes)
    nedges = len(tedges)
    #print( 'nodes from list = ', nnodes)
    
"""
    decrease number of nodes by using edge count
"""
def edge_filter():
    global nnodes, nedges, nodes, edges, wordlist
 
    #print( 'node before edge_filter = ', nnodes, nedges)    
    dic_nodes = dict()
    for i in range(nnodes):
        dic_nodes[nodes[i]] = i

    redges = []                     # edges with random number 
    for edge in edges:
        rand = random()
        entry = (edge, rand)
        redges.append(entry)

    count = itemgetter(1)
    list(map(count,redges))                  
    xedges = sorted(redges, key = count)    # sorted esge list   
    weight = list()
    for i in range(nnodes):
        weight.append(0)
   
    edges.clear()
    nodes.clear()
    for xedge in xedges:
        edge = xedge[0]
        ii = dic_nodes[edge[0]]
        jj = dic_nodes[edge[1]]
        if weight[ii] > MAXEDGE or weight[jj] > MAXEDGE : 
            if edge[0] not in wordlist and edge[1] not in wordlist: continue
        weight[ii] += 1
        weight[jj] += 1
        edges.append(edge)
        if edge[0] not in nodes: nodes.append(edge[0])
        if edge[1] not in nodes: nodes.append(edge[1])
    nnodes = len(nodes)
    nedges = len(edges)        
    #print( 'node after edge_filter = ', nnodes, nedges)   
       
"""
    decrease number of nodes using node weight    
"""
def node_filter():
    global nnodes, nedges, nodes, edges 
    
    nnodes = len(nodes)
    #print( 'node before node_filter = ', nnodes, nedges)
    while nnodes > maxnodes:
        dic_nodes = dict()
        for i in range(nnodes):
            dic_nodes[nodes[i]] = i
             
        weight = list()
        for i in range(nnodes):
            weight.append(0)
        
        for edge in edges:
            ii = dic_nodes[edge[0]]
            jj = dic_nodes[edge[1]]
            weight[ii] += 1
            weight[jj] += 1
        
        minweight = 10000
        for i in range(nnodes):
            if weight[i] < minweight : minweight = weight[i]
                
        minnodes = []
        for i in range(nnodes):
            if weight[i] == minweight:
                minnodes.append(nodes[i])
        for node in minnodes:
            nodes.remove(node)              # remove from nodes - reducing
            
        xedges = edges.copy()
        for edge in xedges:
            src = edge[0]
            dst = edge[1]
            if src in minnodes or dst in minnodes:
                edges.remove(edge)          # remove edges 
        
        # check if more needed - create nodes from edges
        nodes.clear()
        for edge in edges:  
            src = edge[0]
            dst = edge[1]
            if src not in nodes:
                nodes.append(src)
            if dst not in nodes:   
                nodes.append(dst)
    
        nnodes = len(nodes)
        nedges = len(edges)    
    #print('nodes after node_filter =', nnodes, nedges)    
 
"""
    layout of initial node position
"""
def init_layout():
    global cnodes, x, y, r, wt, dcool
    
    dcool = 2 * KF
    nnodes = len(nodes) 
    
    for i in range(nnodes):
        x.append(0)
        y.append(0)
        r.append(0)
        wt.append(0)
    
    dic_nodes.clear()
    cnodes.clear()
   
    for i in range(nnodes):
        wt[i] = 0
        dic_nodes[nodes[i]] = i
        x[i] = randint(0, swidth)
        y[i] = randint(0, sheight)       
        
    for i in range(nedges):
        src = edges[i][0]
        dst = edges[i][1]
        wt[dic_nodes[src]] += 1
        wt[dic_nodes[dst]] += 1       
    render()
    
""" 
    update node position 
"""
def layout():     
    global x, y, r, wt, dcool, delta
        
    KCOOL = 0.95        # ratio per iteration
    DWALL = 100         # pixel from wall
    KWALL = 10          # weight of wall force
    MINDIST =200        # minimum distance for repulse force
    
    def fr(d): return KF * KF /d
    def fa(d): return d * d / KF
                
    dx = list()
    dy = list()
    for i in range(nnodes):
        dx.append(0)
        dy.append(0)

    # repulse force
    for i in range(nnodes):
        for j in range(i+1, nnodes):
            ex = x[i] - x[j]
            ey = y[i] - y[j]
            er = sqrt(ex*ex + ey*ey) 
            ee = er - r[i] - r[j] 
            if ee < 0:  ee = -ee
            if ee > MINDIST : continue
            frep = fr(ee)
            dx[i] += ex/er*frep
            dy[i] += ey/er*frep
            dx[j] -= ex/er*frep
            dy[j] -= ey/er*frep

    # attracting force            
    for edge in edges:
        src = dic_nodes[edge[0]]
        dst = dic_nodes[edge[1]]
        ex = x[src] - x[dst]
        ey = y[src] - y[dst]
        er = sqrt(ex*ex + ey*ey)
        ee = er - r[src] -r[dst]
        if ee < 0 : ee = -ee
        if er < 0.1 : continue
        fatr = fa(ee)
        dx[src] -= ex/er*fatr
        dy[src] -= ey/er*fatr        
        dx[dst] += ex/er*fatr           
        dy[dst] += ey/er*fatr  
  
    for i in range(nnodes):
        if x[i] < DWALL : 
            dx[i] += fa(swidth - x[i]) * KWALL
        elif x[i] > swidth - DWALL : 
            dx[i] -= fa(x[i]) * KWALL
        elif y[i] < DWALL: 
            dy[i] += fa(sheight -y[i]) * KWALL
        elif y[i] > sheight - DWALL: 
            dy[i] -=fa(y[i]) *KWALL 

    delta = 0
    for i in range(nnodes):  
        dr = sqrt( dx[i]*dx[i] + dy[i]*dy[i])        
        if (dr > dcool): dist = dcool     # distance short enough
        else: dist = dr
        dx[i] = dx[i]/dr*dist         # 비례해서 줄임
        dy[i] = dy[i]/dr*dist
        x[i] = x[i] + dx[i]
        y[i] = y[i] + dy[i]        
        delta += fabs(dx[i]) + fabs(dy[i])
    dcool = KCOOL*dcool             # decrease max distance    

"""
    render current nodes    .
"""
def render():
    global wi, ncolor
    wi.scene.clear()
    
    lcolor =  QColor('#CCCCCC') 
    qpen = QPen(lcolor, 1, Qt.SolidLine)
  
    for i in range(nedges):
        src = dic_nodes[edges[i][0]]
        dst = dic_nodes[edges[i][1]]
        x1 = x[src]
        y1 = y[src]
        x2 = x[dst]
        y2 = y[dst]        
        wi.scene.addLine(x1,y1,x2,y2, qpen)
        
    brush = QBrush(QColor('#FFCCDD'))
    
    for i in range(nnodes):
        r[i] = 10. + 3. * sqrt(wt[i])
        if nodes[i] not in dic_type:
            type = '기타'
        else:
            type = dic_type[nodes[i]]
        colornum = dic_num[type]
        bcolor = ncolor[colornum]
        brush = QBrush(QColor(bcolor))
        # create node
        r2 = 2*r[i]
        wi.scene.addEllipse(x[i]-r[i], y[i]-r[i], r2, r2, qpen, brush)        
        
        #full =nodes[i]
        twrap = textwrap.wrap(nodes[i], width = 8)
        nrow = len(twrap)
        for k in range(nrow):        
            txt = wi.scene.addText(twrap[k])
            rect = txt.boundingRect()
            h = rect.height()
            w = rect.width()
            txt.setPos(x[i] - w//2 ,y[i] - h//2 + k*14 - nrow*7 + 7 )
    wi.show()
    
    
#===============================================================
""" update : major routine for explorer
             diferent path for each mode      
             mode can be changed with user input 
             
    mode 0 : normal update with better layout
         1 : repositon with old node data 
         2 : new wordlist ( random/input/click )
         9 : do nonthing, just waiting for user input
"""            
def update():
    global mode, mx, my, x, y, r, flag_click, flag_rclick,wi,flag_self
    if flag_quit : root.destroy() 
    if flag_click: 
        #print('flag_click')
        for i in range(nnodes):
            xx = x[i] - mx
            yy = y[i] - my
            rr = sqrt(xx*xx + yy*yy)
            flag_click = False
            if rr  < r[i] :
                wordlist.clear()
                wordlist.append(nodes[i])
                flag_self = True                
                mode = 2
                if flag_big:
                    url = 'https://ko.wikipedia.org/wiki/'+nodes[i]
                else:
                    url = 'https://ko.m.wikipedia.org/wiki/'+nodes[i]                    
                wi.web.load(QUrl(url))
                wi.web.show()
                wi.pageEdit.setText(nodes[i])
                break

    if flag_rclick: 
        for i in range(nnodes):
            xx = x[i] - mx
            yy = y[i] - my
            rr = sqrt(xx*xx + yy*yy)
            flag_rclick = False
            if rr  < r[i] :
                wordlist.append(nodes[i])
                flag_self = True
                mode = 2
                if flag_big:
                    url = 'https://ko.wikipedia.org/wiki/'+nodes[i]
                else:
                    url = 'https://ko.m.wikipedia.org/wiki/'+nodes[i]  
                wi.web.load(QUrl(url))
                wi.web.show()  
                word = nodes[i]
                pg = wi.pageEdit.text()
                pg = pg + '+' + word
                wi.pageEdit.setText(pg)
                break

    if mode == 2:
        word_to_nodes()
        if nedges > maxedges : edge_filter()
        if nnodes > maxnodes : node_filter()    
        init_layout()
        mode = 0        
    elif mode == 1:
        mode = 0
    if mode != 9:       
        for i in range(20):
            layout()
        render()
        if delta < nnodes : mode = 9        # stable enough, mode change
    wi.timer.setInterval(20)
   
"""
    get five random words and put in wordlist    
"""
def rand_page():
    global mode, flag_self,wi     
    wordlist.clear()
    flag_self = True
    pg = ''
    for i in range(5):
        idx = randint(0,len(allnodes))
        #idx = i       
        word = allnodes[idx]    
        wordlist.append(word)
        pg = pg + '+' + word
    mode = 2
    pg = pg[1:]
    wi.pageEdit.setText(pg)
    if flag_big:
        url = 'https://ko.wikipedia.org/wiki/'+wordlist[0]
    else:
        url = 'https://ko.m.wikipedia.org/wiki/'+wordlist[0]  
    wi.web.load(QUrl(url))   
    
# get slider info and create new layout if necessary                
def reposition():
    global dcool, x, y, mode

    dcool = KF
    for i in range(nnodes):
        x[i] += (random()-0.5)*dcool       
        y[i] += (random()-0.5)*dcool
    mode = 1 

def page_input():
    global mode,wi
    line = str(wi.pageEdit.text())  
    tokens = line.split('+')
    wordlist.clear()
    for i in range(len(tokens)):
        word = tokens[i].strip()
        wordlist.append(word)
    #print (tokens)
    mode = 2
        
def include():
    global flag_self, mode
    flag_self = True
    mode = 2

def exclude():
    global flag_self, mode    
    flag_self = False
    mode =  2


# GraphicsScene with mousePressEvent 

class graphicsScene(QGraphicsScene):

    def __init__ (self, parent=None):
        super(graphicsScene, self).__init__ (parent)

    def mousePressEvent(self, event):
        global flag_click,flag_rclick, mx,my
        point = event.scenePos()      
        mx = point.x()
        my = point.y() 
        if event.button() == Qt.LeftButton:
            flag_click = True       
        else:
            flag_rclick = True
        #print('mouse =', mx,my, flag_click)  

class webView(QWebView):
    def __init__(self,parent=None):
        super(webView,self).__init__(parent)
    
    def link_clicked(self, url):
        global wordlist, mode, wi 
        txt = url.toString()        
        self.load(url)  
        #print('link_clicked',txt)  
        if flag_big and txt[:30] == 'https://ko.wikipedia.org/wiki/':
            word = txt[30:]
        elif not flag_big and txt[:32] == 'https://ko.m.wikipedia.org/wiki/':
            word = txt[32:]
        else : 
            pass
        word = word.replace('_',' ')
        wordlist.clear()
        wordlist.append(word)
        wi.pageEdit.setText(word)
        mode = 2
        self.show()    
        
"""
    main class for Wikiplorer
    Use Qt GUI for web browser 
"""
class Wikiplorer(QWidget):
    global web
    def __init__(self, parent=None):
        super(Wikiplorer, self).__init__(parent)
        self.initUI()
    
    def loadFinished(self):
        #print('load finished', str(self.web.title())[:10])
        self.web.setFocus()
        self.web.show()
     
    def initUI(self):    
        left = QFrame(self)       
        pageLabel = QLabel(' 검색')

        self.pageEdit = QLineEdit()
        self.pageEdit.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)     
        self.connect(self.pageEdit,SIGNAL('returnPressed()'),page_input)
           
        hbox2 = QHBoxLayout()
        hbox2.addWidget(pageLabel)
        hbox2.addWidget(self.pageEdit)

        randButton = QPushButton('랜덤')
        randButton.clicked.connect(rand_page)         
        rdButton = QPushButton('재배치')
        rdButton.clicked.connect(reposition)       
        exButton = QPushButton('검색어 제외')
        exButton.clicked.connect(exclude)
        inButton = QPushButton('검색어 포함')
        inButton.clicked.connect(include)        
            
        hbox3 = QHBoxLayout()
        hbox3.addWidget(randButton)
        hbox3.addWidget(rdButton)
        hbox3.addWidget(exButton)
        hbox3.addWidget(inButton)         
        hbox3.addStretch(1)
        
        view = QGraphicsView()
        self.scene = graphicsScene()                # new graphicsScene
        view.setRenderHint(QPainter.Antialiasing)   # antialiasing 처리 
        view.setScene(self.scene)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox2) 
        vbox.addWidget(view)
        vbox.addLayout(hbox3)
        left.setLayout(vbox)

        hbox = QHBoxLayout(self)
        self.web = webView(self)
        page = self.web.page()
        page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)   
                  
        self.web.linkClicked.connect(self.web.link_clicked)
        self.web.loadFinished.connect(self.loadFinished)            
            
        QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))        
               
        splitter = QSplitter(QtCore.Qt.Horizontal)      
        splitter.addWidget(self.web)
        splitter.addWidget(left)         
        hbox.addWidget(splitter)
        
        splitter.setStretchFactor(0,1)
        splitter.setStretchFactor(1,2)        

        self.setWindowTitle('Wikiplorer [ko]')       
        self.showMaximized()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(update)     
        self.timer.setSingleShot(False)           
        self.timer.start()
        self.show()

        
def sigint_handler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    if QMessageBox.question(None, '', "Are you sure you want to quit?",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No) == QMessageBox.Yes:
        QApplication.quit()
        
def main():
    global web, swidth, sheight, wi, mode, maxnodes, maxedges, flag_big
    read_files()   
    app = QtGui.QApplication(sys.argv)
    wi = Wikiplorer()

    desk = app.desktop()
    rect = desk.geometry()
    swidth = rect.width()//2
    if swidth > 800 : 
        flag_big = True
    else: 
        flag_big = False
    sheight = rect.height() - 200   
    maxnodes = int(swidth*sheight/DENSITY)
    maxedges = maxnodes * 3
    
    mode = 9                # just wait for change
    rand_page()
    word_to_nodes()

    if nedges > maxedges : edge_filter()
    if nnodes > maxnodes : node_filter()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)
    timer = QTimer()
    timer.start(500)  # handle exit function with python 
    timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.
    # Your code here.
    main()
    sys.exit(app.exec_())
    