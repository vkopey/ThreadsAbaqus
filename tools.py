# -*- coding: cp1251 -*-
'''êîìïîíåíòè äëÿ ïîáóäîâè ìîäåë³'''
from math import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
import regionToolset
from visualization import *
from connectorBehavior import *
import subprocess

if _my_thread_model==2: openMdb(pathName='C:/Temp/zamok.cae')
if _my_thread_model==3: openMdb(pathName='C:/Temp/nkt.cae')
model=mdb.models['Model-1']

class Dim:
    "Êëàñ îïèñóº ïîíÿòòÿ ðîçì³ðó"
    n=0.0 #íîì³íàëüíèé ðîçì³ð
    ei=0.0 #íèæíº â³äõèëåííÿ
    es=0.0 #âåðõíº â³äõèëåííÿ
    v=0.0 #ä³éñíå çíà÷åííÿ
    def __init__(self,*x):
        "êîíñòðóêòîð, x-êîðòåæ"
        self.n=x[0][0]
        self.ei=x[0][1]
        self.es=x[0][2]
    def min(self):
        "ïîâåðòàº ì³í³ìàëüíèé ðîçì³ð"
        return self.n+self.ei
    def max(self):
        "ïîâåðòàº ìàêñèìàëüíèé ðîçì³ð"
        return self.n+self.es
class Line(object):
    '''Ë³í³ÿ (â³äð³çîê àáî ïðÿìà)
    p1,p2 - ïåðøà ³ äðóãà òî÷êè
    len - äîâæèíà
    angle - êóò äî 0X â ãðàäóñàõ
    '''
    def __init__(self,p1,p2=None,len=None,angle=None):
        self.p1=p1
        x1,y1=self.p1[0],self.p1[1]
        if len==None and p2==None:
            len=1.0
        if angle!=None:
            angle=radians(angle)
        if p2==None:
            self.p2=(x1+len*cos(angle),y1+len*sin(angle))
        else:
            self.p2=p2
        x2,y2=self.p2[0],self.p2[1]
        #êîåô³ö³ºíòè ð³âíÿííÿ Ax+By+C=0
        self.A=y1-y2
        self.B=x2-x1
        self.C=x1*y2-x2*y1
    def points(self):
        '''ïîâåðòàº x1,y1,x2,y2'''
        return self.p1[0],self.p1[1],self.p2[0],self.p2[1]
    def angleOX(self):
        '''êóò íàõèëó äî ox â ðàä³àíàõ'''
        return atan(-self.A/self.B)    
    def len(self):
        '''äîâæèíà'''
        x1,y1,x2,y2=self.points()
        return sqrt((y2-y1)**2+(x2-x1)**2)
    def x(self,y):
        '''êîîðäèíàòà x òî÷êè ë³í³¿ çà êîîðäèíàòîþ y'''
        x1,y1,x2,y2=self.points()
        return (y-y1)*(x2-x1)/(y2-y1)+x1#x
    def y(self,x):
        '''êîîðäèíàòà y òî÷êè ë³í³¿ çà êîîðäèíàòîþ x'''
        x1,y1,x2,y2=self.points()
        return (x-x1)*(y2-y1)/(x2-x1)+y1#y
    def mpoint(self):
        '''ñåðåäíÿ òî÷êà'''
        x1,y1,x2,y2=self.points()
        return ((x2-x1)/2+x1,(y2-y1)/2+y1)
    def dist(self,point):
        '''â³äñòàíü â³ä ë³í³¿ äî òî÷êè point'''
        x,y=point[0],point[1]
        return abs((self.A*x+self.B*y+self.C)/sqrt(self.A**2+self.B**2))
    def cros_point(self,line):
        '''òî÷êà ïåðåòèíó ç ë³í³ºþ line'''
        x=(self.B*line.C-line.B*self.C)/(self.A*line.B-line.A*self.B)
        y=(self.C*line.A-line.C*self.A)/(self.A*line.B-line.A*self.B)
        return (x,y)
    def drawAbaqus(self,sketch):
        '''ðèñóâàòè â Abaqus'''
        g=sketch.Line(point1=self.p1, point2=self.p2)
        return g
             
class N_angle(object):
    '''N-êóòíèê ç³ ñêðóãëåííÿìè
    L - ñïèñîê ë³í³é (ïî ïîðÿäêó)
    R - ñïèñîê ðàä³óñ³â ñêðóãëåíü (ïî ïîðÿäêó).
    Íàïðèêëàä, R[0] - ñêðóãëåííÿ ì³æ L[0] ³ L[1]
    Ïðèêëàä:
    L1=Line(p1=(1.0,1.0),len=2.0,angle=170)
    cp=Line(p1=L1.p1,angle=90+30).cros_point(Line(p1=L1.p2,angle=90-30))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    T1=N_angle([L1,L2,L3],[0.05,0.05,0.05])
    '''
    def __init__(self,L,R):
        self.N=len(L)#ê³ëüê³ñòü ë³í³é (êóò³â)
        L.append(L[0])#äîáàâèòè â ñïèñîê ë³í³é ïåðøó: [L1,L2,L3,L1]
        self.V=range(self.N)#ñïèñîê âåðøèí
        for i in range(self.N):
            self.V[i]=self.Vert(L[i],L[i+1],R[i])
    def Vert(self,La,Lb,R):
        '''ïîâåðòàº âåðøèíó â ôîðìàò³:
        (òî÷êà, ïåðøà ë³í³ÿ, äðóãà ë³í³ÿ, ðàä³óñ ñêðóãëåííÿ).
        ßêùî ïåðøà òî÷êà ïåðøî¿ ë³í³¿ ñï³âïàäàº ç ïåðøîþ
        àáî äðóãîþ òî÷êîþ äðóãî¿ ë³í³¿, òî âîíà º âåðøèíîþ'''
        if La.p1==Lb.p1 or La.p1==Lb.p2:
            V=(La.p1,La,Lb,R)
        else: V=(Lb.p2,La,Lb,R)
        return V
    def drawAbaqus(self,sketch):
        '''ðèñóâàòè â Abaqus'''
        g=range(self.N)
        for i in range(self.N):#ðèñóâàòè ë³í³¿
            g[i]=self.V[i][1].drawAbaqus(sketch)
        g.append(g[0])#äîáàâèòè â ñïèñîê ë³í³é ïåðøó: [g1,g2,g3,g1]
        for i in range(self.N):#ðèñóâàòè ñêðóãëåííÿ
            if self.V[i][3]!=0:#ÿêùî ðàä³óñ ñêðóãëåííÿ íå 0
                sketch.FilletByRadius(curve1=g[i], curve2=g[i+1], nearPoint1=self.V[i][1].mpoint(), nearPoint2=self.V[i][2].mpoint(), radius=self.V[i][3]) 

class Material:
    '''Êëàñ îïèñóº ïîíÿòòÿ ìàòåð³àëó
    Â Abaqus çàäàºòüñÿ ³ñòèííà ä³àãðàìà äåôîðìóâàííÿ (äèâ.Stress and strain measures)
    E - ìîäóëü ïðóæíîñò³, Ïà
    mu - êîåô³ö³ºíò Ïóàññîíà
    st - ãðàíèöÿ òåêó÷îñò³, Ïà
    et - äåôîðìàö³ÿ äëÿ st
    sb - ³ñòèííà ãðàíèöÿ ì³öíîñò³, Ïà (sv - óìîâíà ãðàíèöÿ)
    eb - ³ñòèííà äåôîðìàö³ÿ, ÿêà â³äïîâ³äàº ãðàíèö³ ì³öíîñò³
    delta - â³äíîñíå âèäîâæåííÿ
    psi - â³äíîñíå çâóæåííÿ
    '''
    def __init__(self,E,mu,st,sv,delta,psi):
        '''êîíñòðóêòîð'''
        self.E=E#ìîäóëü ïðóæíîñò³
        self.mu=mu#êîåô³ö³ºíò Ïóàññîíà
        self.st=st#ãðàíèöÿ òåêó÷îñò³
        self.et=st/E#äåôîðìàö³ÿ äëÿ st
        self.delta=delta/100.0#â³äíîñíå âèäîâæåííÿ ï³ñëÿ ðîçðèâó
        self.psi=psi/100.0#â³äíîñíå çâóæåííÿ ï³ñëÿ ðîçðèâó
        k=0.4#êîåô³ö³ºíò(eb=(0.1...0.4,0.2...0.8)delta)
        self.sv=sv#ãðàíèöÿ ì³öíîñò³
        self.sb=sv*(1+k*self.delta)#³ñòèííà ãðàíèöÿ ì³öíîñò³ 
        self.eb=log(1+k*self.delta)#³ñòèííà äåôîðìàö³ÿ, ÿêà â³äïîâ³äàº ãðàíèö³ ì³öíîñò³
        #³ñòèííå íàïðóæåííÿ ³ äåôîðìàö³ÿ â ìîìåíò ðóéíóâàííÿ
        self.sk=0.8*self.sv/(1-self.psi)#0.8-êîåô³ö³ºíò ðóéíóþ÷îãî íàâàíòàæåííÿ
        #self.sk=self.sv*(1+1.35*self.psi)
        self.ek=log(1/(1-self.psi))
    def bilinear(self):
        '''Ïîâåðòàº ñëîâíèê åëåñòè÷íèõ ³ ïëàñòè÷íèõ âëàñòèâîñòåé'''
        return {'el':((self.E,self.mu),),
                'pl':((self.st,0.0),#á³ë³í³éíà çàëåæí³ñòü
                (self.sb,self.eb))}#àáî (self.sk,self.ek)
    def e(self,s,n):
        '''Ñòåïåíåâà çàëåæí³ñòü e(s)
        n - ñòåï³íü
        '''
        return self.et*(s/self.st)**n
    def power(self,k):
        '''Ïîâåðòàº ñëîâíèê åëåñòè÷íèõ ³ ïëàñòè÷íèõ âëàñòèâîñòåé
        k - ê³ëüê³ñòü ë³í³é äëÿ àïðîêñèìàö³¿ ïëàñòè÷íî¿ ä³ëÿíêè (2,4,8...)
        '''
        #n âèçíà÷àºòüñÿ ç óìîâè ïðîõîäæåííÿ ÷åðåç òî÷êó (eb+et,sb), n=6...10
        n=log((self.eb+self.et)/self.et)/log(self.sb/self.st)
        ds=self.sb-self.st
        #ñòåïåíåâà çàëåæí³ñòü
        k_=float(k)
        s_e=[(self.st+i/k_*ds,self.e(self.st+i/k_*ds,n)-self.et) for i in range(0,k+1)]
        #s_e=[(self.st+i*ds,self.e(self.st+i*ds,n)-self.et) for i in [0.0,0.25,0.5,0.75,1.0]]
        s_e.append((self.sk,self.ek))#äîáàâèòè òî÷êó ðóéíóâàííÿ
        return {'el':((self.E,self.mu),),
                'pl':tuple(s_e)}

matlib={
'40':Material(E=210000.0e+6,mu=0.28,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'40fesafe':Material(E=200000.0e+6,mu=0.33,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'20Í2Ì':Material(E=210000.0e+6,mu=0.28,st=382.0e+6,sv=588.0e+6,delta=21.0,psi=56.0),
'30ÕÌÀ':Material(E=210000.0e+6,mu=0.28,st=392.0e+6,sv=598.0e+6,delta=20.0,psi=62.0),
'15Í3ÌÀ':Material(E=210000.0e+6,mu=0.28,st=490.0e+6,sv=637.0e+6,delta=22.0,psi=60.0),
'15Õ2ÍÌÔ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'15Õ2ÃÌÔ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'14Õ3ÃÌÞ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=725.0e+6,delta=16.0,psi=63.0),
}
steel20={'el':((210000000000.0, 0.28), ),
               'pl':((620000000.0, 0.0),
                     (640000000.0, 0.02),
                     (800000000.0, 0.04),
                     (860000000.0, 0.08),
                     (864000000.0, 0.11))}
steel45={'el':((210000000000.0, 0.28), ),
               'pl':((620000000.0, 0.0),
                     (640000000.0, 0.02),
                     (800000000.0, 0.04),
                     (860000000.0, 0.08),
                     (864000000.0, 0.11))}

def delCutExtrude():
    "Çíèùóº óñ³ åëåìåíòè, íàçâà ÿêèõ ïî÷èíàºòüñÿ ç 'Cut extrude' ³ 'Partition face-1'"
    if model.parts['Part-2'].features.has_key('Partition face-1'):
        del model.parts['Part-2'].features['Partition face-1']  #çíèùóº Partition face
    for f in model.parts['Part-1'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-1'].deleteFeatures((f.name,))
    for f in model.parts['Part-2'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-2'].deleteFeatures((f.name,))
def set_values(sketch,p):
    '''
    Ïðèñâîþº çíà÷åííÿ ïàðàìåòðàì åñê³çà'
    Ïðèêëàä:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values(sketch='nipple',p=par)
    '''
    s=model.sketches[sketch]
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def set_values2(sketch,base,p):
    '''
    Ïðèñâîþº çíà÷åííÿ ïàðàìåòðàì åñê³çà'
    Ïðèêëàä:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values2(sketch='nipple',base='Quad_h',p=par)
    '''
    s=model.ConstrainedSketch(name=sketch, objectToCopy=mdb.models['Model-1'].sketches[base])
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def part_builder(part,sketch='Sketch-1',vector=(0.0,0.0),oper='shell'):
    '''Äîäàº äî äåòàë³ âèð³ç àáî ïîâåðõíþ çàäàíó ºñê³çîì
    Ïðèêëàä:
    part_builder(p, 'groove', (0,0), 'cut')
    '''
    s=model.ConstrainedSketch(name='__profile__',sheetSize=200.)
    part.projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=s)
    s.ConstructionLine(point1=(0.0,0.0), point2=(0.0, 10.0))
    s.retrieveSketch(sketch=model.sketches[sketch])
    s.move(objectList=s.geometry.values(),vector=vector)
    if oper=='shell': part.Shell(sketch=s)
    if oper=='cut': part.Cut(sketch=s)
    del s
def createPart(n,s):
    '''Ñòâîðþº äåòàëü
    n - ³ì'ÿ
    s - åñê³ç
    '''
    model.Part(dimensionality=AXISYMMETRIC, name=n, type=DEFORMABLE_BODY)
    model.parts[n].BaseShell(sketch=model.sketches[s])
def createPart3D(frompart,sketch,part):
    '''Ñòâîðþº 3D äåòàëü íà îñíîâ³ îñåñèìåòðè÷íî¿ äåòàë³
    Ñòâîðþºòüñÿ åñê³ç sketch ÿê ïðîåêö³ÿ îñåñèìåòðè÷íî¿ äåòàë³'''
    s=model.ConstrainedSketch(name=sketch,sheetSize=200.)
    tmp=model.ConstrainedSketch(name='__profile__',sheetSize=200.)
    #s.sketchOptions.setValues(viewStyle=AXISYM)
    model.parts[frompart].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=tmp)
    ln=tmp.ConstructionLine(point1=(0.0,0.0), point2=(0.0, 10.0))
    tmp.FixedConstraint(entity=ln)
    tmp.assignCenterline(line=ln)
    s.retrieveSketch(sketch=tmp)
    #s.sketchOptions.setValues(constructionGeometry=ON)
    p=model.Part(dimensionality=THREE_D, name=part, type=DEFORMABLE_BODY)
    p.BaseSolidRevolve(angle=360.0, flipRevolveDirection=OFF, sketch=s)
def createCut(Part,Sketch,Begin,P,Fi,Len,X,Y,dx,dy):
    '''Ñòâîðþº ÷àñòèíó ïðîô³ëÿ ð³çüáè
    Part - äåòàëü (ðÿäîê)
    Sketch - åñê³ç (ðÿäîê)
    Begin - ïî÷àòîê ð³çüáè (ö³ëå)
    P - êðîê ð³çüáè (ä³éñíå)
    Fi - êóò êîíóñà êîí³÷íî¿ ð³çüáè (ãðàäóñè)
    Len - äîâæèíà ð³çüáè (ä³éñíå)
    X,Y - ïî÷àòêîâ³ êîîðäèíàòè öåíòðà ïðîô³ëþ
    dx - ðàä³àëüíèé íàïðÿìîê ïîäà÷³ (+1 - âïðàâî, -1 - âë³âî)
    dy - îñüîâèé íàïðÿìîê ïîäà÷³ (+1 - ââåðõ, -1 - âíèç)
    '''
    #ìîæíà öå çðîáèòè òàêîæ çà äîïîìîãîþ LinearInstancePattern
    i=Begin#íîìåð âèòêà (0-ïåðøèé)
    while i*P<=Len:#äîâæèíà ð³çüáè
        s=model.ConstrainedSketch(name='__profile__',sheetSize=200.)
        model.parts[Part].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=s)
        s.ConstructionLine(point1=(0.0,0.0), point2=(0.0, 10.0))
        s.retrieveSketch(sketch=model.sketches[Sketch])
        s.delete(objectList=(s.vertices.findAt((0.0,0.0),), ))
        s.move(objectList=s.geometry.values(),vector=(X+dx*P*tan(Fi*pi/180)*i,Y+dy*P*i))
        model.parts[Part].Cut(sketch=s)
        del s
        i=i+1
    return i-1
def createPartition(part,offset):
    '''Ä³ëèòü ïîâåðõíþ äåòàë³ ë³í³ºþ (0.0,offset,0.0), (2000.0,offset,0.0)'''
    model.parts[part].PartitionFaceByShortestPath(faces=
        model.parts[part].faces[0], point1=(0.0,offset,0.0), point2=(2000.0,offset,0.0))
def createPartition3D(part,offset):
    '''Ä³ëèòü îá'ºì äåòàë³ ïëîùèíîþ çì³ùåíîþ â³ä XZPLANE íà â³äñòàíü offset'''
    p = model.parts[part]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offset)
    dp = p.datums.values()[-1]
    p.PartitionCellByDatumPlane(datumPlane=dp, cells=p.cells[0])
def createMaterial(n,et,pt,kinematic=False):
    '''Ñòâîðþº ìàòåð³àë
    n - ³ì'ÿ
    et - ïðóæí³ õàðàêòåðèñòèêè
    pt - ïëàñòè÷í³ õàðàêòåðèñòèêè
    kinematic - ìîäåëü çì³öíåííÿ (True - ê³íåìàòè÷íå, False - ³çîòðîïíå)
    '''
    m=model.Material(name=n)
    m.Elastic(table=et)
    if kinematic:
        m.Plastic(hardening=KINEMATIC, table=pt)# pt - ò³ëüêè äâ³ òî÷êè !
    else:
        m.Plastic(table=pt)

def createSectionAssign(n,m,p):
    '''Ñòâîðþº ³ ïðèñâîþº ñåêö³¿ äåòàë³
    n - ³ì'ÿ
    m - ìàòåð³àë
    p - äåòàëü
    '''
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(
        faces=model.parts[p].faces), sectionName=n)
def createSectionAssign3D(n,m,p):
    '''Ñòâîðþº ³ ïðèñâîþº ñåêö³¿ äåòàë³
    n - ³ì'ÿ
    m - ìàòåð³àë
    p - äåòàëü
    '''
    if model.parts[p].sectionAssignments:
        del model.parts[p].sectionAssignments[0]
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(cells=model.parts[p].cells), sectionName=n) 

def createAssemblyInstance(n,p):
    '''Ñòâîðþº åëåìåíò çáîðêè
    n - ³ì'ÿ
    p - äåòàëü
    '''
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createAssemblyInstance3D(n,p):
    '''Ñòâîðþº åëåìåíò çáîðêè
    n - ³ì'ÿ
    p - äåòàëü
    '''
    #model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createStep(n,pr):
    '''Ñòâîðþº êðîê
    n - ³ì'ÿ
    pr - ïîïåðåäí³é êðîê
    '''
    model.StaticStep(name=n, previous=pr)
def createContactSet(n,i,ep):
    '''Ñòâîðþº íàá³ð äëÿ êîíòàêòó
    n - ³ì'ÿ
    i - åëåìåíò çáîðêè
    ep - êîðòåæ òî÷îê êðîìîê íå äëÿ êîíòàêòó
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].edges
    e=ae.findAt(*ep)#*ep - ðîçïàêóâàííÿ êîðòåæó
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,edges=ae.findAt(*p))
def createContactSet3D(n,i,ep):
    '''Ñòâîðþº íàá³ð äëÿ êîíòàêòó
    n - ³ì'ÿ
    i - åëåìåíò çáîðêè
    ep - êîðòåæ òî÷îê êðîìîê íå äëÿ êîíòàêòó
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].faces
    e=ae.findAt(*ep)#*ep - ðîçïàêóâàííÿ êîðòåæó
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,faces=ae.findAt(*p))
def createContactProperty():
    '''Ñòâîðþº âëàñòèâîñò³ êîíòàêòó'''
    model.ContactProperty('IntProp-1')
    model.interactionProperties['IntProp-1'].TangentialBehavior(
        dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None,
        formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION,
        pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF,
        table=((0.05, ), ), temperatureDependency=OFF)
    model.interactionProperties['IntProp-1'].NormalBehavior(
        allowSeparation=ON, constraintEnforcementMethod=DEFAULT,pressureOverclosure=HARD)
def createContact():
    '''Ñòâîðþº êîíòàêò'''
    sm=model.rootAssembly.sets['Master']
    ss=model.rootAssembly.sets['Slave']
    #model.SurfaceToSurfaceContactStd(adjustMethod=NONE,
    #    clearanceRegion=None, createStepName='Step-1', datumAxis=None,
    #    initialClearance=OMIT, interactionProperty='IntProp-1', interferenceType=
    #    SHRINK_FIT, master=Region(side1Edges=sm.edges), name='Int-1',
    #    slave=Region(side1Edges=ss.edges), sliding=FINITE, smooth=0.2)
    model.SurfaceToSurfaceContactStd(adjustMethod=NONE, 
        clearanceRegion=None, createStepName='Step-1', datumAxis=None, enforcement=
        SURFACE_TO_SURFACE, initialClearance=OMIT, interactionProperty='IntProp-1', 
        interferenceType=SHRINK_FIT, master=Region(side1Edges=sm.edges), name='Int-1',
        slave=Region(side1Edges=ss.edges), sliding=SMALL, surfaceSmoothing=NONE,
        thickness=ON) 
def createContact3D():
    '''Ñòâîðþº êîíòàêò'''
    sm=model.rootAssembly.sets['Master']
    ss=model.rootAssembly.sets['Slave']
    model.SurfaceToSurfaceContactStd(adjustMethod=NONE, 
        clearanceRegion=None, createStepName='Step-1', datumAxis=None, 
        initialClearance=OMIT, interactionProperty='IntProp-1', master=Region(
        side1Faces=sm.faces), name='Int-1', slave=Region(
        side1Faces=ss.faces), sliding=FINITE, smooth=0.2) 
def createBCSet(n,i,ep):
    '''Ñòâîðþº íàá³ð äëÿ ãðàíè÷íî¿ óìîâè
    n - ³ì'ÿ
    i - åëåìåíò çáîðêè
    ep - êîðòåæ òî÷îê êðîìîê äëÿ ãðàíè÷íî¿ óìîâè
    '''
    s=model.rootAssembly.Set(edges=model.rootAssembly.instances[i].edges.findAt(ep), name=n)
def createBCSet3D(n,i,ep):
    '''Ñòâîðþº íàá³ð äëÿ ãðàíè÷íî¿ óìîâè
    n - ³ì'ÿ
    i - åëåìåíò çáîðêè
    ep - êîðòåæ òî÷îê êðîìîê äëÿ ãðàíè÷íî¿ óìîâè
    '''
    s=model.rootAssembly.Set(faces=model.rootAssembly.instances[i].faces.findAt(ep), name=n)
    
def createBC_Pressure(step):
    '''Ñòâîðþº òèñê. Ïðèêëàä:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Edges=s.edges))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])    
def createBC_Axis():
    '''Ñòâîðþº ãðàíè÷í³ óìîâè íà îñ³ (äëÿ îñåñèìåòðè÷íèõ ìîäåëåé)'''
    s=model.rootAssembly.sets['Axis']
    model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'Axis', region=Region(edges=s.edges), u1=0.0, u2=UNSET, ur3=0.0)
def createBC_Encastre():
    '''Ñòâîðþº çàêð³ïëåííÿ'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(edges=s.edges))
def createBC_BoltLoad(part,point,value):
    '''Ñòâîðþº BoltLoad. Ïðèêëàä:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Edges=model.rootAssembly.instances[part].edges.findAt((point, ))))
def createBC_Pressure3D(step):
    '''Ñòâîðþº òèñê. Ïðèêëàä:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Faces=s.faces))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])
def createBC_Encastre3D():
    '''Ñòâîðþº çàêð³ïëåííÿ'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(faces=s.faces))
def createBC_BoltLoad3D(part,point,value):
    '''Ñòâîðþº BoltLoad. Ïðèêëàä:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Faces=model.rootAssembly.instances[part].faces.findAt((point, ))))
def createMesh():
    '''Ñòâîðþº ñ³òêó'''
    model.rootAssembly.seedPartInstance(deviationFactor=0.1,
        regions=(model.rootAssembly.instances['Part-1-1'],
        model.rootAssembly.instances['Part-2-1']), size=2.6)
    sm=model.rootAssembly.sets['Master']
    ss=model.rootAssembly.sets['Slave']
    model.rootAssembly.seedEdgeByNumber(edges=sm.edges, number=4)
    model.rootAssembly.seedEdgeByNumber(edges=ss.edges, number=4)
    model.rootAssembly.generateMesh(regions=(
        model.rootAssembly.instances['Part-1-1'],
        model.rootAssembly.instances['Part-2-1']))
def createMesh3D():
    '''Ñòâîðþº ñ³òêó'''
    model.rootAssembly.setMeshControls(elemShape=TET, regions=
        model.rootAssembly.instances['Part-3-1'].cells+\
        model.rootAssembly.instances['Part-4-1'].cells, technique=FREE)
    model.rootAssembly.seedPartInstance(deviationFactor=0.1, 
        regions=(model.rootAssembly.instances['Part-3-1'], 
        model.rootAssembly.instances['Part-4-1']), size=2.8)
    model.rootAssembly.generateMesh(regions=(
        model.rootAssembly.instances['Part-3-1'], 
        model.rootAssembly.instances['Part-4-1'])) 
def createEdgesSet(n, i, p, exclude=False):
    '''Ñòâîðþº Set ç ðåáåð (ðåáðî çàäàºòüñÿ äîâ³ëüíîþ òî÷êîþ íà íüîìó)
    exclude=True - ç óñ³õ ðåáåð êð³ì çàäàíèõ (ò³ëüêè äëÿ OdbSet!)
    createEdgesSet(n='Set-6',i='Part-1-1',p=((enr1, ),(en1, )))'''
    if exclude==True:
        edges=model.rootAssembly.instances[i].edges[:]
        xEdges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, xEdges=xEdges, name=n)
    else:
        edges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, name=n)
def createVerticesSet(n, i, p):
    '''Ñòâîðþº Set ç âåðøèí
    createVerticesSet(n='Set-7',i='Part-1-1',p=(((0,0,0), ),))'''
    model.rootAssembly.Set(vertices=model.rootAssembly.instances[i].vertices.findAt(*p), name=n)
def createSet(n, r):
    '''Ñòâîðþº Set ç ðåã³îíó
    r = regionToolset.Region(edges=e,vertices=v,xEdges=xe,xVertices=xv)
    createSet(n='Set-8', r=r)'''
    model.rootAssembly.Set(region=r, name=n)
def delItems():
    '''Çíèùóº åëåìåíòè'''
    if model.steps.has_key('Step-2'): del model.steps['Step-2']
    if model.steps.has_key('Step-1'): del model.steps['Step-1']
def createJobSubmit():
    '''Ñòâîðþº çàäà÷ó ³ âèêîíóº ¿¿'''
    myJob = mdb.Job(name=model.name, model=model.name)
    myJob.submit()
    # ×åêàòè ïîêè çàäà÷à íå áóäå ðîçâ'ÿçàíà
    myJob.waitForCompletion()
def createObdNodeSet(coords,name='MYSET',prt='Part-1-1',item_type='vertex'):
    '''Ñòâîðþº ObdNodeSet çà çàäàíèì êîîðäèíàòàìè ðåáðîì àáî âåðøèíîþ'''
    if item_type=='edge':
        _item=model.rootAssembly.instances[prt].edges.findAt(coordinates=coords)
        #àáî getClosest()
    if item_type=='vertex':
        _item=model.rootAssembly.instances[prt].vertices.findAt(coordinates=coords)   
    _nodes=_item.getNodes() #model.rootAssembly.sets['Set-6'].nodes
    _nodeLabels=[]
    for x in _nodes:
        _nodeLabels.append(x.label)
    _nset=myOdb.rootAssembly.NodeSetFromNodeLabels(name=name,nodeLabels=((prt.upper(), _nodeLabels),))
def readODB_path(path,step,var,intersections=False):
    '''×èòàº ðåçóëüòàòè ç îñòàííüîãî ôðåéìó êðîêó íà çàäàíîìó øëÿõó ç òî÷îê
    path - øëÿõ (ñïèñîê òî÷îê, >=1)
    step - êðîê
    var - çì³ííà:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Pressure'), )), )
    (('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), )), )
    (('U', NODAL, ((INVARIANT, 'Magnitude'), )), )
    (('U', NODAL, ((COMPONENT, 'U1'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    'D' #êîåô³ö³ºíò çàïàñó âòîìíî¿ ì³öíîñò³
    intersections=True - äîäàº ïðîì³æí³ òî÷êè
    Ïðèêëàä: readODB_path(path=((1.97212e+001,  3.65000e+001, 0.0), ),step='Step-1',var=var)
    '''
    pth=session.Path(name='Path-tmp', type=POINT_LIST, expression=path) #øëÿõ
    if var=='D':
        frame1 = session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[0]
        session.viewports['Viewport: 1'].odbDisplay.setFrame(frame=frame1) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections, shape=UNDEFORMED, labelType=SEQ_ID) 
    else:
        st=myOdb.steps[step].number-1 #³íäåêñ êðîêó
        fr=len(myOdb.steps[step].frames)-1 #³íäåêñ îñòàííüîãî ôðåéìó
        #session.viewports['Viewport: 1'].odbDisplay.setFrame(step=st, frame=fr)
        #session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 'Tresca')) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections,shape=UNDEFORMED, labelType=SEQ_ID,step=st,frame=fr,variable=var) #äàí³
    res=[] #ñïèñîê ðåçóëüòàò³â
    for x in dat.data:
        res.append(x[1]) #äîäàòè äî ñïèñêó ðåçóëüòàò³â
    #âèäàëèòè òèì÷àñîâ³ äàí³
    del session.paths['Path-tmp']
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k]  
    return res #ïîâåðòàå ñïèñîê çíà÷åíü

def readODB_set(set,step,var,pos=NODAL):
    '''×èòàº ðåçóëüòàòè ç îñòàííüîãî ôðåéìó êðîêó íà çàäàí³é ìíîæèí³
    set - ìíîæèíà
    step - êðîê
    var - çì³ííà:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    pos - ïîçèö³ÿ: NODAL - äëÿ âóçë³â,INTEGRATION_POINT - äëÿ åëåìåíò³â
    Ïðèêëàä: readODB_set(set='Cont',step='Step-1',var=var)
    '''
    if pos==NODAL:    
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #äàí³
    if pos==INTEGRATION_POINT:
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=INTEGRATION_POINT, variable=var, elementSets=(set.upper(),)) #äàí³
    res=[] #ñïèñîê ðåçóëüòàò³â
    for x in dat: #äëÿ âñ³õ âóçë³â
        n=0
        for k in myOdb.steps.keys(): #äëÿ âñ³õ êðîê³â
            n=n+len(myOdb.steps[k].frames) #ñóìàðíà ê³ëüê³ñòü ôðåéì³â äî k êðîêó âêëþ÷íî
            if k==step: res.append(x.data[n-1][1]) #äîäàòè äî ñïèñêó ðåçóëüòàò³â
            #data öå ((÷àñ,çíà÷åííÿ),(÷àñ,çíà÷åííÿ)...)
    #âèäàëèòè òèì÷àñîâ³ äàí³
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #ïîâåðòàå ñïèñîê çíà÷åíü

def readODB_set_(set,var):
    '''Ïîâåðòàº ñïèñîê ðåçóëüòàò³â â âóçëàõ çàäàíî¿ ìíîæèíè
    (äëÿ çì³ííèõ fe-safe)
    set - ìíîæèíà
    var - çì³ííà:
    (('LOGLife-Repeats', ELEMENT_NODAL), )
    (('FOS@Life=Infinite', ELEMENT_NODAL), )
    (('%%Failure@Life=5E6-Repeats', ELEMENT_NODAL), )
    Ïðèêëàä: readODB_set_(set='Set-1',var=var)
    '''
    #îòðèìàòè äàí³
    dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #äàí³
    
    res=[] #ñïèñîê ðåçóëüòàò³â
    for x in dat: #äëÿ âñ³õ âóçë³â
        #x.data öå ((÷àñ,çíà÷åííÿ),(÷àñ,çíà÷åííÿ)...)
        res.append(x.data) #äàí³
                            
    #âèäàëèòè òèì÷àñîâ³ äàí³
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #ïîâåðòàå ñïèñîê çíà÷åíü

def readODB_set2(set,step,var,pos=NODAL):
    '''×èòàº ðåçóëüòàòè ç îñòàííüîãî ôðåéìó êðîêó íà çàäàí³é ìíîæèí³
    (ìåíø óí³âåðñàëüíà àëüòåðíàòèâà readODB_set())
    set - ìíîæèíà
    step - êðîê
    var - çì³ííà:
    ('S','Mises')
    ('S','Pressure')
    ('U','Magnitude')
    ('U','U1')
    ('CPRESS','')
    ('D','') #êîåô³ö³ºíò çàïàñó âòîìíî¿ ì³öíîñò³
    pos - ïîçèö³ÿ: NODAL - äëÿ âóçë³â,INTEGRATION_POINT - äëÿ åëåìåíò³â
    Ïðèêëàä: readODB_set2(set='Cont',step='Step-1',var=('S','Mises'))
    '''
    if pos==NODAL:    
        s=myOdb.rootAssembly.nodeSets[set.upper()] #ìíîæèíà âóçë³â
    if pos==INTEGRATION_POINT:
        s=myOdb.rootAssembly.elementSets[set.upper()] #ìíîæèíà åëåìåíò³â
    if var[0]=='D': 
        fo=session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[-1].fieldOutputs['D'].getSubset(region=s,position=pos) #äàí³
    else:
        fo=myOdb.steps[step].frames[-1].fieldOutputs[var[0]].getSubset(region=s,position=pos) #äàí³
        #openOdb(r'C:/Temp/Model-1.odb').steps['Step-1'].frames[4].fieldOutputs['CPRESS'].getSubset(position=NODAL, region=openOdb(r'C:/Temp/Model-1.odb').rootAssembly.nodeSets['CONT']).values[0].data
    res=[] #ñïèñîê ðåçóëüòàò³â
    for v in fo.values: #äëÿ êîæíîãî âóçëà/åëåìåíòà
        if var[1]=='Mises': res.append(v.mises)#äîäàòè äî ñïèñêó ðåçóëüòàò³â
        if var[1]=='Pressure': res.append(v.press)
        if var[0]=='U' and var[1]=='Magnitude': res.append(v.magnitude)
        if var[1]=='U1': res.append(v.data.tolist()[0])
        if var[1]=='U2': res.append(v.data.tolist()[1])
        if var[0]=='CPRESS': res.append(v.data)
        if var[0]=='D': res.append(v.data)
    return res #ïîâåðòàå ñïèñîê çíà÷åíü

def runFeSafe(input_odb,input_stlx,output_odb):
    '''Âèêîíóº àíàë³ç âòîìíî¿ ì³öíîñò³ ó fe-safe
    input_odb - íàçâà âõ³äíîãî ôàéëó ðåçóëüòàò³â Abaqus (áåç ðîçøèðåííÿ .odb)
    input_stlx - íàçâà ôàéëó ìîäåë³ fe-safe (áåç ðîçøèðåííÿ .stlx)
    output_odb - íàçâà âèõ³äíîãî ôàéëó ðåçóëüòàò³â Abaqus (áåç ðîçøèðåííÿ .odb)
    ßêùî ç FEA ìîäåë³ ³ìïîðòóþòüñÿ íàïðóæåííÿ ³ äåôîðìàö³¿, òî ïåðåä ñòâîðåííÿì ôàéëó sltx â íàëàøòóâàííÿõ Analysis Options íåîáõ³äíî âèáðàòè Read strains from FE Models.
    '''
    s=r'd:\Program Files\Safe_Technology\fe-safe\version.6.2\exe\fe-safe_cl.exe -s j=c:\1\{iodb}.odb b=c:\1\{istlx}.stlx o=c:\1\{oodb}.odb'
    s=s.format(iodb=input_odb, istlx=input_stlx, oodb=output_odb)
    # âèêîíóº îá÷èñëåííÿ â fe-safe òà ÷åêàº çàâåðøåííÿ
    subprocess.Popen(s).communicate()
    
def writeLDFfile(filename,lst):
    '''Çì³íþº âì³ñò ôàéëó âèçíà÷åííÿ íàâàíòàæåííÿ LDF fe-safe
    filename - ³ìÿ ôàéëó
    lst - ñïèñîê ðÿäê³â-äàíèõ
    '''
    f=open(filename, "w")
    s="""
# .ldf file created by fe-safe compliant product 6.2-01[mswin]

INIT
transitions=Yes
END

# Block number 1
BLOCK n=1, scale=1
lh=0 1 , ds=1, scale=1
lh=0 {x} , ds=2, scale=1
END

""" # øàáëîí ôàéëó
    s=s.format(x=lst[0]) # âì³ñò ôàéëó ç øàáëîíó
    f.write(s)
    f.close()
    
def SF_field(s1='Step-1',s2='Step-2',Sn=207000000,m=1):
    '''Ðîçðàõîâóº ïîëå êîåô³ö³ºíòà çàïàñó âòîìíî¿ ì³öíîñò³ çà êðèòåð³ºì Ñàéíñà''' 
        
    S3_2 = myOdb.steps[s2].frames[-1].fieldOutputs['S'].getScalarField(invariant=MAX_PRINCIPAL)
    S3_1 = myOdb.steps[s1].frames[-1].fieldOutputs['S'].getScalarField(invariant=MAX_PRINCIPAL)
    Sm3=(S3_2+S3_1)/2
    Sa3=(S3_2-S3_1)/2
    
    S2_2 = myOdb.steps[s2].frames[-1].fieldOutputs['S'].getScalarField(invariant=MID_PRINCIPAL)
    S2_1 = myOdb.steps[s1].frames[-1].fieldOutputs['S'].getScalarField(invariant=MID_PRINCIPAL)
    Sm2=(S2_2+S2_1)/2
    Sa2=(S2_2-S2_1)/2
    
    S1_2 = myOdb.steps[s2].frames[-1].fieldOutputs['S'].getScalarField(invariant=MIN_PRINCIPAL)
    S1_1 = myOdb.steps[s1].frames[-1].fieldOutputs['S'].getScalarField(invariant=MIN_PRINCIPAL)
    Sm1=(S1_2+S1_1)/2
    Sa1=(S1_2-S1_1)/2
    
    D =(Sn-m*(Sm1+Sm2+Sm3)/3)/power(((power((Sa1-Sa2), 2)+power((Sa2-Sa3), 2)+power((Sa3-Sa1), 2))/2), 0.5)
    
    scratchOdb = session.ScratchOdb(odb=myOdb)
    sessionStep = scratchOdb.Step(name='Session Step',description='Step for Viewer non-persistent fields',domain=TIME,timePeriod=1.0)
    sessionFrame = sessionStep.Frame(frameId=0, frameValue=0.0, description='Session Frame')
    sessionField = sessionFrame.FieldOutput(name='D', description='D', field=D)  
def saveDB(name):
    import shutil,os,shelve
    if not os.path.exists('MyDB'):
        os.mkdir('MyDB')
    shutil.copyfile(model.name + '.odb', 'MyDB/'+name+'.odb')#êîï³þâàòè ôàéë
    
    my_db = shelve.open("MyDB/mydb")#â³äêðèòè ôàéë ïîëèö³
    my_db[name]=[mat1,mat2,d,d_n]#çàïèñàòè ó ïîëèöþ ï³ä êëþ÷åì name
    my_db.close()#çàêðèòè ôàéë ïîëèö³
def readDB(name):
    import shelve
    my_db = shelve.open("MyDB/mydb")#â³äêðèòè ôàéë ïîëèö³
    print my_db.keys()#âèâåñòè ñïèñîê óñ³õ êëþ÷³â
    if my_db.has_key(name):#ÿêùî º êëþ÷ name
        print my_db[name]
    my_db.close()#çàêðèòè ôàéë ïîëèö³
