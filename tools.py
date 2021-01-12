# -*- coding: cp1251 -*-
'''компоненти для побудови моделі'''
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
    "Клас описує поняття розміру"
    n=0.0 #номінальний розмір
    ei=0.0 #нижнє відхилення
    es=0.0 #верхнє відхилення
    v=0.0 #дійсне значення
    def __init__(self,*x):
        "конструктор, x-кортеж"
        self.n=x[0][0]
        self.ei=x[0][1]
        self.es=x[0][2]
    def min(self):
        "повертає мінімальний розмір"
        return self.n+self.ei
    def max(self):
        "повертає максимальний розмір"
        return self.n+self.es
class Line(object):
    '''Лінія (відрізок або пряма)
    p1,p2 - перша і друга точки
    len - довжина
    angle - кут до 0X в градусах
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
        #коефіцієнти рівняння Ax+By+C=0
        self.A=y1-y2
        self.B=x2-x1
        self.C=x1*y2-x2*y1
    def points(self):
        '''повертає x1,y1,x2,y2'''
        return self.p1[0],self.p1[1],self.p2[0],self.p2[1]
    def angleOX(self):
        '''кут нахилу до ox в радіанах'''
        return atan(-self.A/self.B)    
    def len(self):
        '''довжина'''
        x1,y1,x2,y2=self.points()
        return sqrt((y2-y1)**2+(x2-x1)**2)
    def x(self,y):
        '''координата x точки лінії за координатою y'''
        x1,y1,x2,y2=self.points()
        return (y-y1)*(x2-x1)/(y2-y1)+x1#x
    def y(self,x):
        '''координата y точки лінії за координатою x'''
        x1,y1,x2,y2=self.points()
        return (x-x1)*(y2-y1)/(x2-x1)+y1#y
    def mpoint(self):
        '''середня точка'''
        x1,y1,x2,y2=self.points()
        return ((x2-x1)/2+x1,(y2-y1)/2+y1)
    def dist(self,point):
        '''відстань від лінії до точки point'''
        x,y=point[0],point[1]
        return abs((self.A*x+self.B*y+self.C)/sqrt(self.A**2+self.B**2))
    def cros_point(self,line):
        '''точка перетину з лінією line'''
        x=(self.B*line.C-line.B*self.C)/(self.A*line.B-line.A*self.B)
        y=(self.C*line.A-line.C*self.A)/(self.A*line.B-line.A*self.B)
        return (x,y)
    def drawAbaqus(self,sketch):
        '''рисувати в Abaqus'''
        g=sketch.Line(point1=self.p1, point2=self.p2)
        return g
             
class N_angle(object):
    '''N-кутник зі скругленнями
    L - список ліній (по порядку)
    R - список радіусів скруглень (по порядку).
    Наприклад, R[0] - скруглення між L[0] і L[1]
    Приклад:
    L1=Line(p1=(1.0,1.0),len=2.0,angle=170)
    cp=Line(p1=L1.p1,angle=90+30).cros_point(Line(p1=L1.p2,angle=90-30))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    T1=N_angle([L1,L2,L3],[0.05,0.05,0.05])
    '''
    def __init__(self,L,R):
        self.N=len(L)#кількість ліній (кутів)
        L.append(L[0])#добавити в список ліній першу: [L1,L2,L3,L1]
        self.V=range(self.N)#список вершин
        for i in range(self.N):
            self.V[i]=self.Vert(L[i],L[i+1],R[i])
    def Vert(self,La,Lb,R):
        '''повертає вершину в форматі:
        (точка, перша лінія, друга лінія, радіус скруглення).
        Якщо перша точка першої лінії співпадає з першою
        або другою точкою другої лінії, то вона є вершиною'''
        if La.p1==Lb.p1 or La.p1==Lb.p2:
            V=(La.p1,La,Lb,R)
        else: V=(Lb.p2,La,Lb,R)
        return V
    def drawAbaqus(self,sketch):
        '''рисувати в Abaqus'''
        g=range(self.N)
        for i in range(self.N):#рисувати лінії
            g[i]=self.V[i][1].drawAbaqus(sketch)
        g.append(g[0])#добавити в список ліній першу: [g1,g2,g3,g1]
        for i in range(self.N):#рисувати скруглення
            if self.V[i][3]!=0:#якщо радіус скруглення не 0
                sketch.FilletByRadius(curve1=g[i], curve2=g[i+1], nearPoint1=self.V[i][1].mpoint(), nearPoint2=self.V[i][2].mpoint(), radius=self.V[i][3]) 

class Material:
    '''Клас описує поняття матеріалу
    В Abaqus задається істинна діаграма деформування (див.Stress and strain measures)
    E - модуль пружності, Па
    mu - коефіцієнт Пуассона
    st - границя текучості, Па
    et - деформація для st
    sb - істинна границя міцності, Па (sv - умовна границя)
    eb - істинна деформація, яка відповідає границі міцності
    delta - відносне видовження
    psi - відносне звуження
    '''
    def __init__(self,E,mu,st,sv,delta,psi):
        '''конструктор'''
        self.E=E#модуль пружності
        self.mu=mu#коефіцієнт Пуассона
        self.st=st#границя текучості
        self.et=st/E#деформація для st
        self.delta=delta/100.0#відносне видовження після розриву
        self.psi=psi/100.0#відносне звуження після розриву
        k=0.4#коефіцієнт(eb=(0.1...0.4,0.2...0.8)delta)
        self.sv=sv#границя міцності
        self.sb=sv*(1+k*self.delta)#істинна границя міцності 
        self.eb=log(1+k*self.delta)#істинна деформація, яка відповідає границі міцності
        #істинне напруження і деформація в момент руйнування
        self.sk=0.8*self.sv/(1-self.psi)#0.8-коефіцієнт руйнуючого навантаження
        #self.sk=self.sv*(1+1.35*self.psi)
        self.ek=log(1/(1-self.psi))
    def bilinear(self):
        '''Повертає словник елестичних і пластичних властивостей'''
        return {'el':((self.E,self.mu),),
                'pl':((self.st,0.0),#білінійна залежність
                (self.sb,self.eb))}#або (self.sk,self.ek)
    def e(self,s,n):
        '''Степенева залежність e(s)
        n - степінь
        '''
        return self.et*(s/self.st)**n
    def power(self,k):
        '''Повертає словник елестичних і пластичних властивостей
        k - кількість ліній для апроксимації пластичної ділянки (2,4,8...)
        '''
        #n визначається з умови проходження через точку (eb+et,sb), n=6...10
        n=log((self.eb+self.et)/self.et)/log(self.sb/self.st)
        ds=self.sb-self.st
        #степенева залежність
        k_=float(k)
        s_e=[(self.st+i/k_*ds,self.e(self.st+i/k_*ds,n)-self.et) for i in range(0,k+1)]
        #s_e=[(self.st+i*ds,self.e(self.st+i*ds,n)-self.et) for i in [0.0,0.25,0.5,0.75,1.0]]
        s_e.append((self.sk,self.ek))#добавити точку руйнування
        return {'el':((self.E,self.mu),),
                'pl':tuple(s_e)}

matlib={
'40':Material(E=210000.0e+6,mu=0.28,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'40fesafe':Material(E=200000.0e+6,mu=0.33,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'20Н2М':Material(E=210000.0e+6,mu=0.28,st=382.0e+6,sv=588.0e+6,delta=21.0,psi=56.0),
'30ХМА':Material(E=210000.0e+6,mu=0.28,st=392.0e+6,sv=598.0e+6,delta=20.0,psi=62.0),
'15Н3МА':Material(E=210000.0e+6,mu=0.28,st=490.0e+6,sv=637.0e+6,delta=22.0,psi=60.0),
'15Х2НМФ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'15Х2ГМФ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'14Х3ГМЮ':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=725.0e+6,delta=16.0,psi=63.0),
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
    "Знищує усі елементи, назва яких починається з 'Cut extrude' і 'Partition face-1'"
    if model.parts['Part-2'].features.has_key('Partition face-1'):
        del model.parts['Part-2'].features['Partition face-1']  #знищує Partition face
    for f in model.parts['Part-1'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-1'].deleteFeatures((f.name,))
    for f in model.parts['Part-2'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-2'].deleteFeatures((f.name,))
def set_values(sketch,p):
    '''
    Присвоює значення параметрам ескіза'
    Приклад:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values(sketch='nipple',p=par)
    '''
    s=model.sketches[sketch]
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def set_values2(sketch,base,p):
    '''
    Присвоює значення параметрам ескіза'
    Приклад:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values2(sketch='nipple',base='Quad_h',p=par)
    '''
    s=model.ConstrainedSketch(name=sketch, objectToCopy=mdb.models['Model-1'].sketches[base])
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def part_builder(part,sketch='Sketch-1',vector=(0.0,0.0),oper='shell'):
    '''Додає до деталі виріз або поверхню задану єскізом
    Приклад:
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
    '''Створює деталь
    n - ім'я
    s - ескіз
    '''
    model.Part(dimensionality=AXISYMMETRIC, name=n, type=DEFORMABLE_BODY)
    model.parts[n].BaseShell(sketch=model.sketches[s])
def createPart3D(frompart,sketch,part):
    '''Створює 3D деталь на основі осесиметричної деталі
    Створюється ескіз sketch як проекція осесиметричної деталі'''
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
    '''Створює частину профіля різьби
    Part - деталь (рядок)
    Sketch - ескіз (рядок)
    Begin - початок різьби (ціле)
    P - крок різьби (дійсне)
    Fi - кут конуса конічної різьби (градуси)
    Len - довжина різьби (дійсне)
    X,Y - початкові координати центра профілю
    dx - радіальний напрямок подачі (+1 - вправо, -1 - вліво)
    dy - осьовий напрямок подачі (+1 - вверх, -1 - вниз)
    '''
    #можна це зробити також за допомогою LinearInstancePattern
    i=Begin#номер витка (0-перший)
    while i*P<=Len:#довжина різьби
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
    '''Ділить поверхню деталі лінією (0.0,offset,0.0), (2000.0,offset,0.0)'''
    model.parts[part].PartitionFaceByShortestPath(faces=
        model.parts[part].faces[0], point1=(0.0,offset,0.0), point2=(2000.0,offset,0.0))
def createPartition3D(part,offset):
    '''Ділить об'єм деталі площиною зміщеною від XZPLANE на відстань offset'''
    p = model.parts[part]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offset)
    dp = p.datums.values()[-1]
    p.PartitionCellByDatumPlane(datumPlane=dp, cells=p.cells[0])
def createMaterial(n,et,pt,kinematic=False):
    '''Створює матеріал
    n - ім'я
    et - пружні характеристики
    pt - пластичні характеристики
    kinematic - модель зміцнення (True - кінематичне, False - ізотропне)
    '''
    m=model.Material(name=n)
    m.Elastic(table=et)
    if kinematic:
        m.Plastic(hardening=KINEMATIC, table=pt)# pt - тільки дві точки !
    else:
        m.Plastic(table=pt)

def createSectionAssign(n,m,p):
    '''Створює і присвоює секції деталі
    n - ім'я
    m - матеріал
    p - деталь
    '''
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(
        faces=model.parts[p].faces), sectionName=n)
def createSectionAssign3D(n,m,p):
    '''Створює і присвоює секції деталі
    n - ім'я
    m - матеріал
    p - деталь
    '''
    if model.parts[p].sectionAssignments:
        del model.parts[p].sectionAssignments[0]
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(cells=model.parts[p].cells), sectionName=n) 

def createAssemblyInstance(n,p):
    '''Створює елемент зборки
    n - ім'я
    p - деталь
    '''
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createAssemblyInstance3D(n,p):
    '''Створює елемент зборки
    n - ім'я
    p - деталь
    '''
    #model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createStep(n,pr):
    '''Створює крок
    n - ім'я
    pr - попередній крок
    '''
    model.StaticStep(name=n, previous=pr)
def createContactSet(n,i,ep):
    '''Створює набір для контакту
    n - ім'я
    i - елемент зборки
    ep - кортеж точок кромок не для контакту
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].edges
    e=ae.findAt(*ep)#*ep - розпакування кортежу
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,edges=ae.findAt(*p))
def createContactSet3D(n,i,ep):
    '''Створює набір для контакту
    n - ім'я
    i - елемент зборки
    ep - кортеж точок кромок не для контакту
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].faces
    e=ae.findAt(*ep)#*ep - розпакування кортежу
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,faces=ae.findAt(*p))
def createContactProperty():
    '''Створює властивості контакту'''
    model.ContactProperty('IntProp-1')
    model.interactionProperties['IntProp-1'].TangentialBehavior(
        dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None,
        formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION,
        pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF,
        table=((0.05, ), ), temperatureDependency=OFF)
    model.interactionProperties['IntProp-1'].NormalBehavior(
        allowSeparation=ON, constraintEnforcementMethod=DEFAULT,pressureOverclosure=HARD)
def createContact():
    '''Створює контакт'''
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
    '''Створює контакт'''
    sm=model.rootAssembly.sets['Master']
    ss=model.rootAssembly.sets['Slave']
    model.SurfaceToSurfaceContactStd(adjustMethod=NONE, 
        clearanceRegion=None, createStepName='Step-1', datumAxis=None, 
        initialClearance=OMIT, interactionProperty='IntProp-1', master=Region(
        side1Faces=sm.faces), name='Int-1', slave=Region(
        side1Faces=ss.faces), sliding=FINITE, smooth=0.2) 
def createBCSet(n,i,ep):
    '''Створює набір для граничної умови
    n - ім'я
    i - елемент зборки
    ep - кортеж точок кромок для граничної умови
    '''
    s=model.rootAssembly.Set(edges=model.rootAssembly.instances[i].edges.findAt(ep), name=n)
def createBCSet3D(n,i,ep):
    '''Створює набір для граничної умови
    n - ім'я
    i - елемент зборки
    ep - кортеж точок кромок для граничної умови
    '''
    s=model.rootAssembly.Set(faces=model.rootAssembly.instances[i].faces.findAt(ep), name=n)
    
def createBC_Pressure(step):
    '''Створює тиск. Приклад:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Edges=s.edges))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])    
def createBC_Axis():
    '''Створює граничні умови на осі (для осесиметричних моделей)'''
    s=model.rootAssembly.sets['Axis']
    model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'Axis', region=Region(edges=s.edges), u1=0.0, u2=UNSET, ur3=0.0)
def createBC_Encastre():
    '''Створює закріплення'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(edges=s.edges))
def createBC_BoltLoad(part,point,value):
    '''Створює BoltLoad. Приклад:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Edges=model.rootAssembly.instances[part].edges.findAt((point, ))))
def createBC_Pressure3D(step):
    '''Створює тиск. Приклад:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Faces=s.faces))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])
def createBC_Encastre3D():
    '''Створює закріплення'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(faces=s.faces))
def createBC_BoltLoad3D(part,point,value):
    '''Створює BoltLoad. Приклад:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Faces=model.rootAssembly.instances[part].faces.findAt((point, ))))
def createMesh():
    '''Створює сітку'''
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
    '''Створює сітку'''
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
    '''Створює Set з ребер (ребро задається довільною точкою на ньому)
    exclude=True - з усіх ребер крім заданих (тільки для OdbSet!)
    createEdgesSet(n='Set-6',i='Part-1-1',p=((enr1, ),(en1, )))'''
    if exclude==True:
        edges=model.rootAssembly.instances[i].edges[:]
        xEdges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, xEdges=xEdges, name=n)
    else:
        edges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, name=n)
def createVerticesSet(n, i, p):
    '''Створює Set з вершин
    createVerticesSet(n='Set-7',i='Part-1-1',p=(((0,0,0), ),))'''
    model.rootAssembly.Set(vertices=model.rootAssembly.instances[i].vertices.findAt(*p), name=n)
def createSet(n, r):
    '''Створює Set з регіону
    r = regionToolset.Region(edges=e,vertices=v,xEdges=xe,xVertices=xv)
    createSet(n='Set-8', r=r)'''
    model.rootAssembly.Set(region=r, name=n)
def delItems():
    '''Знищує елементи'''
    if model.steps.has_key('Step-2'): del model.steps['Step-2']
    if model.steps.has_key('Step-1'): del model.steps['Step-1']
def createJobSubmit():
    '''Створює задачу і виконує її'''
    myJob = mdb.Job(name=model.name, model=model.name)
    myJob.submit()
    # Чекати поки задача не буде розв'язана
    myJob.waitForCompletion()
def createObdNodeSet(coords,name='MYSET',prt='Part-1-1',item_type='vertex'):
    '''Створює ObdNodeSet за заданим координатами ребром або вершиною'''
    if item_type=='edge':
        _item=model.rootAssembly.instances[prt].edges.findAt(coordinates=coords)
        #або getClosest()
    if item_type=='vertex':
        _item=model.rootAssembly.instances[prt].vertices.findAt(coordinates=coords)   
    _nodes=_item.getNodes() #model.rootAssembly.sets['Set-6'].nodes
    _nodeLabels=[]
    for x in _nodes:
        _nodeLabels.append(x.label)
    _nset=myOdb.rootAssembly.NodeSetFromNodeLabels(name=name,nodeLabels=((prt.upper(), _nodeLabels),))
def readODB_path(path,step,var,intersections=False):
    '''Читає результати з останнього фрейму кроку на заданому шляху з точок
    path - шлях (список точок, >=1)
    step - крок
    var - змінна:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Pressure'), )), )
    (('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), )), )
    (('U', NODAL, ((INVARIANT, 'Magnitude'), )), )
    (('U', NODAL, ((COMPONENT, 'U1'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    'D' #коефіцієнт запасу втомної міцності
    intersections=True - додає проміжні точки
    Приклад: readODB_path(path=((1.97212e+001,  3.65000e+001, 0.0), ),step='Step-1',var=var)
    '''
    pth=session.Path(name='Path-tmp', type=POINT_LIST, expression=path) #шлях
    if var=='D':
        frame1 = session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[0]
        session.viewports['Viewport: 1'].odbDisplay.setFrame(frame=frame1) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections, shape=UNDEFORMED, labelType=SEQ_ID) 
    else:
        st=myOdb.steps[step].number-1 #індекс кроку
        fr=len(myOdb.steps[step].frames)-1 #індекс останнього фрейму
        #session.viewports['Viewport: 1'].odbDisplay.setFrame(step=st, frame=fr)
        #session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 'Tresca')) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections,shape=UNDEFORMED, labelType=SEQ_ID,step=st,frame=fr,variable=var) #дані
    res=[] #список результатів
    for x in dat.data:
        res.append(x[1]) #додати до списку результатів
    #видалити тимчасові дані
    del session.paths['Path-tmp']
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k]  
    return res #повертае список значень

def readODB_set(set,step,var,pos=NODAL):
    '''Читає результати з останнього фрейму кроку на заданій множині
    set - множина
    step - крок
    var - змінна:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    pos - позиція: NODAL - для вузлів,INTEGRATION_POINT - для елементів
    Приклад: readODB_set(set='Cont',step='Step-1',var=var)
    '''
    if pos==NODAL:    
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #дані
    if pos==INTEGRATION_POINT:
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=INTEGRATION_POINT, variable=var, elementSets=(set.upper(),)) #дані
    res=[] #список результатів
    for x in dat: #для всіх вузлів
        n=0
        for k in myOdb.steps.keys(): #для всіх кроків
            n=n+len(myOdb.steps[k].frames) #сумарна кількість фреймів до k кроку включно
            if k==step: res.append(x.data[n-1][1]) #додати до списку результатів
            #data це ((час,значення),(час,значення)...)
    #видалити тимчасові дані
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #повертае список значень

def readODB_set_(set,var):
    '''Повертає список результатів в вузлах заданої множини
    (для змінних fe-safe)
    set - множина
    var - змінна:
    (('LOGLife-Repeats', ELEMENT_NODAL), )
    (('FOS@Life=Infinite', ELEMENT_NODAL), )
    (('%%Failure@Life=5E6-Repeats', ELEMENT_NODAL), )
    Приклад: readODB_set_(set='Set-1',var=var)
    '''
    #отримати дані
    dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #дані
    
    res=[] #список результатів
    for x in dat: #для всіх вузлів
        #x.data це ((час,значення),(час,значення)...)
        res.append(x.data) #дані
                            
    #видалити тимчасові дані
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #повертае список значень

def readODB_set2(set,step,var,pos=NODAL):
    '''Читає результати з останнього фрейму кроку на заданій множині
    (менш універсальна альтернатива readODB_set())
    set - множина
    step - крок
    var - змінна:
    ('S','Mises')
    ('S','Pressure')
    ('U','Magnitude')
    ('U','U1')
    ('CPRESS','')
    ('D','') #коефіцієнт запасу втомної міцності
    pos - позиція: NODAL - для вузлів,INTEGRATION_POINT - для елементів
    Приклад: readODB_set2(set='Cont',step='Step-1',var=('S','Mises'))
    '''
    if pos==NODAL:    
        s=myOdb.rootAssembly.nodeSets[set.upper()] #множина вузлів
    if pos==INTEGRATION_POINT:
        s=myOdb.rootAssembly.elementSets[set.upper()] #множина елементів
    if var[0]=='D': 
        fo=session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[-1].fieldOutputs['D'].getSubset(region=s,position=pos) #дані
    else:
        fo=myOdb.steps[step].frames[-1].fieldOutputs[var[0]].getSubset(region=s,position=pos) #дані
        #openOdb(r'C:/Temp/Model-1.odb').steps['Step-1'].frames[4].fieldOutputs['CPRESS'].getSubset(position=NODAL, region=openOdb(r'C:/Temp/Model-1.odb').rootAssembly.nodeSets['CONT']).values[0].data
    res=[] #список результатів
    for v in fo.values: #для кожного вузла/елемента
        if var[1]=='Mises': res.append(v.mises)#додати до списку результатів
        if var[1]=='Pressure': res.append(v.press)
        if var[0]=='U' and var[1]=='Magnitude': res.append(v.magnitude)
        if var[1]=='U1': res.append(v.data.tolist()[0])
        if var[1]=='U2': res.append(v.data.tolist()[1])
        if var[0]=='CPRESS': res.append(v.data)
        if var[0]=='D': res.append(v.data)
    return res #повертае список значень

def runFeSafe(input_odb,input_stlx,output_odb):
    '''Виконує аналіз втомної міцності у fe-safe
    input_odb - назва вхідного файлу результатів Abaqus (без розширення .odb)
    input_stlx - назва файлу моделі fe-safe (без розширення .stlx)
    output_odb - назва вихідного файлу результатів Abaqus (без розширення .odb)
    Якщо з FEA моделі імпортуються напруження і деформації, то перед створенням файлу sltx в налаштуваннях Analysis Options необхідно вибрати Read strains from FE Models.
    '''
    s=r'd:\Program Files\Safe_Technology\fe-safe\version.6.2\exe\fe-safe_cl.exe -s j=c:\1\{iodb}.odb b=c:\1\{istlx}.stlx o=c:\1\{oodb}.odb'
    s=s.format(iodb=input_odb, istlx=input_stlx, oodb=output_odb)
    # виконує обчислення в fe-safe та чекає завершення
    subprocess.Popen(s).communicate()
    
def writeLDFfile(filename,lst):
    '''Змінює вміст файлу визначення навантаження LDF fe-safe
    filename - імя файлу
    lst - список рядків-даних
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

""" # шаблон файлу
    s=s.format(x=lst[0]) # вміст файлу з шаблону
    f.write(s)
    f.close()
    
def SF_field(s1='Step-1',s2='Step-2',Sn=207000000,m=1):
    '''Розраховує поле коефіцієнта запасу втомної міцності за критерієм Сайнса''' 
        
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
    shutil.copyfile(model.name + '.odb', 'MyDB/'+name+'.odb')#копіювати файл
    
    my_db = shelve.open("MyDB/mydb")#відкрити файл полиці
    my_db[name]=[mat1,mat2,d,d_n]#записати у полицю під ключем name
    my_db.close()#закрити файл полиці
def readDB(name):
    import shelve
    my_db = shelve.open("MyDB/mydb")#відкрити файл полиці
    print my_db.keys()#вивести список усіх ключів
    if my_db.has_key(name):#якщо є ключ name
        print my_db[name]
    my_db.close()#закрити файл полиці
