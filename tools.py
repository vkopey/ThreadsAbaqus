# -*- coding: cp1251 -*-
'''���������� ��� �������� �����'''
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
    "���� ����� ������� ������"
    n=0.0 #���������� �����
    ei=0.0 #���� ���������
    es=0.0 #����� ���������
    v=0.0 #����� ��������
    def __init__(self,*x):
        "�����������, x-������"
        self.n=x[0][0]
        self.ei=x[0][1]
        self.es=x[0][2]
    def min(self):
        "������� ��������� �����"
        return self.n+self.ei
    def max(self):
        "������� ������������ �����"
        return self.n+self.es
class Line(object):
    '''˳�� (������ ��� �����)
    p1,p2 - ����� � ����� �����
    len - �������
    angle - ��� �� 0X � ��������
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
        #����������� ������� Ax+By+C=0
        self.A=y1-y2
        self.B=x2-x1
        self.C=x1*y2-x2*y1
    def points(self):
        '''������� x1,y1,x2,y2'''
        return self.p1[0],self.p1[1],self.p2[0],self.p2[1]
    def angleOX(self):
        '''��� ������ �� ox � �������'''
        return atan(-self.A/self.B)    
    def len(self):
        '''�������'''
        x1,y1,x2,y2=self.points()
        return sqrt((y2-y1)**2+(x2-x1)**2)
    def x(self,y):
        '''���������� x ����� �� �� ����������� y'''
        x1,y1,x2,y2=self.points()
        return (y-y1)*(x2-x1)/(y2-y1)+x1#x
    def y(self,x):
        '''���������� y ����� �� �� ����������� x'''
        x1,y1,x2,y2=self.points()
        return (x-x1)*(y2-y1)/(x2-x1)+y1#y
    def mpoint(self):
        '''������� �����'''
        x1,y1,x2,y2=self.points()
        return ((x2-x1)/2+x1,(y2-y1)/2+y1)
    def dist(self,point):
        '''������� �� �� �� ����� point'''
        x,y=point[0],point[1]
        return abs((self.A*x+self.B*y+self.C)/sqrt(self.A**2+self.B**2))
    def cros_point(self,line):
        '''����� �������� � ��� line'''
        x=(self.B*line.C-line.B*self.C)/(self.A*line.B-line.A*self.B)
        y=(self.C*line.A-line.C*self.A)/(self.A*line.B-line.A*self.B)
        return (x,y)
    def drawAbaqus(self,sketch):
        '''�������� � Abaqus'''
        g=sketch.Line(point1=self.p1, point2=self.p2)
        return g
             
class N_angle(object):
    '''N-������ � ������������
    L - ������ ��� (�� �������)
    R - ������ ������ ��������� (�� �������).
    ���������, R[0] - ���������� �� L[0] � L[1]
    �������:
    L1=Line(p1=(1.0,1.0),len=2.0,angle=170)
    cp=Line(p1=L1.p1,angle=90+30).cros_point(Line(p1=L1.p2,angle=90-30))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    T1=N_angle([L1,L2,L3],[0.05,0.05,0.05])
    '''
    def __init__(self,L,R):
        self.N=len(L)#������� ��� (����)
        L.append(L[0])#�������� � ������ ��� �����: [L1,L2,L3,L1]
        self.V=range(self.N)#������ ������
        for i in range(self.N):
            self.V[i]=self.Vert(L[i],L[i+1],R[i])
    def Vert(self,La,Lb,R):
        '''������� ������� � ������:
        (�����, ����� ���, ����� ���, ����� ����������).
        ���� ����� ����� ����� �� ������� � ������
        ��� ������ ������ ����� ��, �� ���� � ��������'''
        if La.p1==Lb.p1 or La.p1==Lb.p2:
            V=(La.p1,La,Lb,R)
        else: V=(Lb.p2,La,Lb,R)
        return V
    def drawAbaqus(self,sketch):
        '''�������� � Abaqus'''
        g=range(self.N)
        for i in range(self.N):#�������� ��
            g[i]=self.V[i][1].drawAbaqus(sketch)
        g.append(g[0])#�������� � ������ ��� �����: [g1,g2,g3,g1]
        for i in range(self.N):#�������� ����������
            if self.V[i][3]!=0:#���� ����� ���������� �� 0
                sketch.FilletByRadius(curve1=g[i], curve2=g[i+1], nearPoint1=self.V[i][1].mpoint(), nearPoint2=self.V[i][2].mpoint(), radius=self.V[i][3]) 

class Material:
    '''���� ����� ������� ��������
    � Abaqus �������� ������� ������� ������������ (���.Stress and strain measures)
    E - ������ ��������, ��
    mu - ���������� ��������
    st - ������� ��������, ��
    et - ���������� ��� st
    sb - ������� ������� ������, �� (sv - ������ �������)
    eb - ������� ����������, ��� ������� ������� ������
    delta - ������� ����������
    psi - ������� ��������
    '''
    def __init__(self,E,mu,st,sv,delta,psi):
        '''�����������'''
        self.E=E#������ ��������
        self.mu=mu#���������� ��������
        self.st=st#������� ��������
        self.et=st/E#���������� ��� st
        self.delta=delta/100.0#������� ���������� ���� �������
        self.psi=psi/100.0#������� �������� ���� �������
        k=0.4#����������(eb=(0.1...0.4,0.2...0.8)delta)
        self.sv=sv#������� ������
        self.sb=sv*(1+k*self.delta)#������� ������� ������ 
        self.eb=log(1+k*self.delta)#������� ����������, ��� ������� ������� ������
        #������� ���������� � ���������� � ������ ����������
        self.sk=0.8*self.sv/(1-self.psi)#0.8-���������� ���������� ������������
        #self.sk=self.sv*(1+1.35*self.psi)
        self.ek=log(1/(1-self.psi))
    def bilinear(self):
        '''������� ������� ���������� � ���������� ������������'''
        return {'el':((self.E,self.mu),),
                'pl':((self.st,0.0),#������ ���������
                (self.sb,self.eb))}#��� (self.sk,self.ek)
    def e(self,s,n):
        '''��������� ��������� e(s)
        n - ������
        '''
        return self.et*(s/self.st)**n
    def power(self,k):
        '''������� ������� ���������� � ���������� ������������
        k - ������� ��� ��� ������������ ��������� ������ (2,4,8...)
        '''
        #n ����������� � ����� ����������� ����� ����� (eb+et,sb), n=6...10
        n=log((self.eb+self.et)/self.et)/log(self.sb/self.st)
        ds=self.sb-self.st
        #��������� ���������
        k_=float(k)
        s_e=[(self.st+i/k_*ds,self.e(self.st+i/k_*ds,n)-self.et) for i in range(0,k+1)]
        #s_e=[(self.st+i*ds,self.e(self.st+i*ds,n)-self.et) for i in [0.0,0.25,0.5,0.75,1.0]]
        s_e.append((self.sk,self.ek))#�������� ����� ����������
        return {'el':((self.E,self.mu),),
                'pl':tuple(s_e)}

matlib={
'40':Material(E=210000.0e+6,mu=0.28,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'40fesafe':Material(E=200000.0e+6,mu=0.33,st=314.0e+6,sv=559.0e+6,delta=16.0,psi=45.0),
'20�2�':Material(E=210000.0e+6,mu=0.28,st=382.0e+6,sv=588.0e+6,delta=21.0,psi=56.0),
'30���':Material(E=210000.0e+6,mu=0.28,st=392.0e+6,sv=598.0e+6,delta=20.0,psi=62.0),
'15�3��':Material(E=210000.0e+6,mu=0.28,st=490.0e+6,sv=637.0e+6,delta=22.0,psi=60.0),
'15�2���':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'15�2���':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=686.0e+6,delta=16.0,psi=63.0),
'14�3���':Material(E=210000.0e+6,mu=0.28,st=617.0e+6,sv=725.0e+6,delta=16.0,psi=63.0),
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
    "����� �� ��������, ����� ���� ���������� � 'Cut extrude' � 'Partition face-1'"
    if model.parts['Part-2'].features.has_key('Partition face-1'):
        del model.parts['Part-2'].features['Partition face-1']  #����� Partition face
    for f in model.parts['Part-1'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-1'].deleteFeatures((f.name,))
    for f in model.parts['Part-2'].features.values():
        if f.name[:11]=='Cut extrude': model.parts['Part-2'].deleteFeatures((f.name,))
def set_values(sketch,p):
    '''
    �������� �������� ���������� �����'
    �������:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values(sketch='nipple',p=par)
    '''
    s=model.sketches[sketch]
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def set_values2(sketch,base,p):
    '''
    �������� �������� ���������� �����'
    �������:
    par={'aint':0,'aext':0,'Rint':0,'Rext':dn.v,'len':l1n.v+20}
    set_values2(sketch='nipple',base='Quad_h',p=par)
    '''
    s=model.ConstrainedSketch(name=sketch, objectToCopy=mdb.models['Model-1'].sketches[base])
    for k,v in p.iteritems():
        s.parameters[k].setValues(expression=str(v))
def part_builder(part,sketch='Sketch-1',vector=(0.0,0.0),oper='shell'):
    '''���� �� ����� ���� ��� �������� ������ ������
    �������:
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
    '''������� ������
    n - ��'�
    s - ����
    '''
    model.Part(dimensionality=AXISYMMETRIC, name=n, type=DEFORMABLE_BODY)
    model.parts[n].BaseShell(sketch=model.sketches[s])
def createPart3D(frompart,sketch,part):
    '''������� 3D ������ �� ����� ������������� �����
    ����������� ���� sketch �� �������� ������������� �����'''
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
    '''������� ������� ������� �����
    Part - ������ (�����)
    Sketch - ���� (�����)
    Begin - ������� ����� (����)
    P - ���� ����� (�����)
    Fi - ��� ������ ������ ����� (�������)
    Len - ������� ����� (�����)
    X,Y - �������� ���������� ������ �������
    dx - ��������� �������� ������ (+1 - ������, -1 - ����)
    dy - ������� �������� ������ (+1 - �����, -1 - ����)
    '''
    #����� �� ������� ����� �� ��������� LinearInstancePattern
    i=Begin#����� ����� (0-������)
    while i*P<=Len:#������� �����
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
    '''ĳ���� �������� ����� ��� (0.0,offset,0.0), (2000.0,offset,0.0)'''
    model.parts[part].PartitionFaceByShortestPath(faces=
        model.parts[part].faces[0], point1=(0.0,offset,0.0), point2=(2000.0,offset,0.0))
def createPartition3D(part,offset):
    '''ĳ���� ��'�� ����� �������� ������� �� XZPLANE �� ������� offset'''
    p = model.parts[part]
    p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=offset)
    dp = p.datums.values()[-1]
    p.PartitionCellByDatumPlane(datumPlane=dp, cells=p.cells[0])
def createMaterial(n,et,pt,kinematic=False):
    '''������� �������
    n - ��'�
    et - ����� ��������������
    pt - �������� ��������������
    kinematic - ������ �������� (True - ����������, False - ���������)
    '''
    m=model.Material(name=n)
    m.Elastic(table=et)
    if kinematic:
        m.Plastic(hardening=KINEMATIC, table=pt)# pt - ����� �� ����� !
    else:
        m.Plastic(table=pt)

def createSectionAssign(n,m,p):
    '''������� � �������� ������ �����
    n - ��'�
    m - �������
    p - ������
    '''
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(
        faces=model.parts[p].faces), sectionName=n)
def createSectionAssign3D(n,m,p):
    '''������� � �������� ������ �����
    n - ��'�
    m - �������
    p - ������
    '''
    if model.parts[p].sectionAssignments:
        del model.parts[p].sectionAssignments[0]
    model.HomogeneousSolidSection(material=m, name=n, thickness=None)
    model.parts[p].SectionAssignment(region=Region(cells=model.parts[p].cells), sectionName=n) 

def createAssemblyInstance(n,p):
    '''������� ������� ������
    n - ��'�
    p - ������
    '''
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createAssemblyInstance3D(n,p):
    '''������� ������� ������
    n - ��'�
    p - ������
    '''
    #model.rootAssembly.DatumCsysByDefault(CARTESIAN)
    model.rootAssembly.Instance(dependent=OFF, name=n, part=model.parts[p])
def createStep(n,pr):
    '''������� ����
    n - ��'�
    pr - ��������� ����
    '''
    model.StaticStep(name=n, previous=pr)
def createContactSet(n,i,ep):
    '''������� ���� ��� ��������
    n - ��'�
    i - ������� ������
    ep - ������ ����� ������ �� ��� ��������
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].edges
    e=ae.findAt(*ep)#*ep - ������������ �������
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,edges=ae.findAt(*p))
def createContactSet3D(n,i,ep):
    '''������� ���� ��� ��������
    n - ��'�
    i - ������� ������
    ep - ������ ����� ������ �� ��� ��������
    '''
    model.rootAssembly.regenerate()
    ae=model.rootAssembly.instances[i].faces
    e=ae.findAt(*ep)#*ep - ������������ �������
    p=[x.pointOn for x in ae if x not in e]
    model.rootAssembly.Set(name=n,faces=ae.findAt(*p))
def createContactProperty():
    '''������� ���������� ��������'''
    model.ContactProperty('IntProp-1')
    model.interactionProperties['IntProp-1'].TangentialBehavior(
        dependencies=0, directionality=ISOTROPIC, elasticSlipStiffness=None,
        formulation=PENALTY, fraction=0.005, maximumElasticSlip=FRACTION,
        pressureDependency=OFF, shearStressLimit=None, slipRateDependency=OFF,
        table=((0.05, ), ), temperatureDependency=OFF)
    model.interactionProperties['IntProp-1'].NormalBehavior(
        allowSeparation=ON, constraintEnforcementMethod=DEFAULT,pressureOverclosure=HARD)
def createContact():
    '''������� �������'''
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
    '''������� �������'''
    sm=model.rootAssembly.sets['Master']
    ss=model.rootAssembly.sets['Slave']
    model.SurfaceToSurfaceContactStd(adjustMethod=NONE, 
        clearanceRegion=None, createStepName='Step-1', datumAxis=None, 
        initialClearance=OMIT, interactionProperty='IntProp-1', master=Region(
        side1Faces=sm.faces), name='Int-1', slave=Region(
        side1Faces=ss.faces), sliding=FINITE, smooth=0.2) 
def createBCSet(n,i,ep):
    '''������� ���� ��� �������� �����
    n - ��'�
    i - ������� ������
    ep - ������ ����� ������ ��� �������� �����
    '''
    s=model.rootAssembly.Set(edges=model.rootAssembly.instances[i].edges.findAt(ep), name=n)
def createBCSet3D(n,i,ep):
    '''������� ���� ��� �������� �����
    n - ��'�
    i - ������� ������
    ep - ������ ����� ������ ��� �������� �����
    '''
    s=model.rootAssembly.Set(faces=model.rootAssembly.instances[i].faces.findAt(ep), name=n)
    
def createBC_Pressure(step):
    '''������� ����. �������:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Edges=s.edges))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])    
def createBC_Axis():
    '''������� ������� ����� �� �� (��� �������������� �������)'''
    s=model.rootAssembly.sets['Axis']
    model.DisplacementBC(amplitude=UNSET, createStepName='Step-1',
    distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
    'Axis', region=Region(edges=s.edges), u1=0.0, u2=UNSET, ur3=0.0)
def createBC_Encastre():
    '''������� ����������'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(edges=s.edges))
def createBC_BoltLoad(part,point,value):
    '''������� BoltLoad. �������:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Edges=model.rootAssembly.instances[part].edges.findAt((point, ))))
def createBC_Pressure3D(step):
    '''������� ����. �������:
    createBC_Pressure([('Step-1',-1.0),('Step-2',-276.0e+6*d0.v**2/dn.v**2)])'''
    s=model.rootAssembly.sets['Pressure']
    model.Pressure(amplitude=UNSET, createStepName=step[0][0],
        distributionType=UNIFORM, field='', magnitude=step[0][1], name='Pressure',
        region=Region(side1Faces=s.faces))
    for x in step:
        model.loads['Pressure'].setValuesInStep(magnitude=x[1], stepName=x[0])
def createBC_Encastre3D():
    '''������� ����������'''
    s=model.rootAssembly.sets['Encastre']
    model.EncastreBC(createStepName='Step-1', name='Encastre', region=Region(faces=s.faces))
def createBC_BoltLoad3D(part,point,value):
    '''������� BoltLoad. �������:
    createBC_BoltLoad('Part-2-1',em3,-0.1)'''
    model.BoltLoad(boltMethod=ADJUST_LENGTH, createStepName='Step-1', datumAxis=
        model.rootAssembly.instances[part].datums[1],
        magnitude=value, name='BoltLoad', region=Region(
        side1Faces=model.rootAssembly.instances[part].faces.findAt((point, ))))
def createMesh():
    '''������� ����'''
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
    '''������� ����'''
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
    '''������� Set � ����� (����� �������� �������� ������ �� �����)
    exclude=True - � ��� ����� ��� ������� (����� ��� OdbSet!)
    createEdgesSet(n='Set-6',i='Part-1-1',p=((enr1, ),(en1, )))'''
    if exclude==True:
        edges=model.rootAssembly.instances[i].edges[:]
        xEdges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, xEdges=xEdges, name=n)
    else:
        edges=model.rootAssembly.instances[i].edges.findAt(*p)
        model.rootAssembly.Set(edges=edges, name=n)
def createVerticesSet(n, i, p):
    '''������� Set � ������
    createVerticesSet(n='Set-7',i='Part-1-1',p=(((0,0,0), ),))'''
    model.rootAssembly.Set(vertices=model.rootAssembly.instances[i].vertices.findAt(*p), name=n)
def createSet(n, r):
    '''������� Set � ������
    r = regionToolset.Region(edges=e,vertices=v,xEdges=xe,xVertices=xv)
    createSet(n='Set-8', r=r)'''
    model.rootAssembly.Set(region=r, name=n)
def delItems():
    '''����� ��������'''
    if model.steps.has_key('Step-2'): del model.steps['Step-2']
    if model.steps.has_key('Step-1'): del model.steps['Step-1']
def createJobSubmit():
    '''������� ������ � ������ ��'''
    myJob = mdb.Job(name=model.name, model=model.name)
    myJob.submit()
    # ������ ���� ������ �� ���� ����'�����
    myJob.waitForCompletion()
def createObdNodeSet(coords,name='MYSET',prt='Part-1-1',item_type='vertex'):
    '''������� ObdNodeSet �� ������� ������������ ������ ��� ��������'''
    if item_type=='edge':
        _item=model.rootAssembly.instances[prt].edges.findAt(coordinates=coords)
        #��� getClosest()
    if item_type=='vertex':
        _item=model.rootAssembly.instances[prt].vertices.findAt(coordinates=coords)   
    _nodes=_item.getNodes() #model.rootAssembly.sets['Set-6'].nodes
    _nodeLabels=[]
    for x in _nodes:
        _nodeLabels.append(x.label)
    _nset=myOdb.rootAssembly.NodeSetFromNodeLabels(name=name,nodeLabels=((prt.upper(), _nodeLabels),))
def readODB_path(path,step,var,intersections=False):
    '''���� ���������� � ���������� ������ ����� �� �������� ����� � �����
    path - ���� (������ �����, >=1)
    step - ����
    var - �����:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Pressure'), )), )
    (('S', INTEGRATION_POINT, ((COMPONENT, 'S11'), )), )
    (('U', NODAL, ((INVARIANT, 'Magnitude'), )), )
    (('U', NODAL, ((COMPONENT, 'U1'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    'D' #���������� ������ ������ ������
    intersections=True - ���� ������ �����
    �������: readODB_path(path=((1.97212e+001,  3.65000e+001, 0.0), ),step='Step-1',var=var)
    '''
    pth=session.Path(name='Path-tmp', type=POINT_LIST, expression=path) #����
    if var=='D':
        frame1 = session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[0]
        session.viewports['Viewport: 1'].odbDisplay.setFrame(frame=frame1) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections, shape=UNDEFORMED, labelType=SEQ_ID) 
    else:
        st=myOdb.steps[step].number-1 #������ �����
        fr=len(myOdb.steps[step].frames)-1 #������ ���������� ������
        #session.viewports['Viewport: 1'].odbDisplay.setFrame(step=st, frame=fr)
        #session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 'Tresca')) 
        dat=session.XYDataFromPath(name='XYData-1', path=pth, includeIntersections=intersections,shape=UNDEFORMED, labelType=SEQ_ID,step=st,frame=fr,variable=var) #���
    res=[] #������ ����������
    for x in dat.data:
        res.append(x[1]) #������ �� ������ ����������
    #�������� �������� ���
    del session.paths['Path-tmp']
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k]  
    return res #�������� ������ �������

def readODB_set(set,step,var,pos=NODAL):
    '''���� ���������� � ���������� ������ ����� �� ������ ������
    set - �������
    step - ����
    var - �����:
    (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), )
    (('CPRESS', ELEMENT_NODAL), )
    pos - �������: NODAL - ��� �����,INTEGRATION_POINT - ��� ��������
    �������: readODB_set(set='Cont',step='Step-1',var=var)
    '''
    if pos==NODAL:    
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #���
    if pos==INTEGRATION_POINT:
        dat=session.xyDataListFromField(odb=myOdb, outputPosition=INTEGRATION_POINT, variable=var, elementSets=(set.upper(),)) #���
    res=[] #������ ����������
    for x in dat: #��� ��� �����
        n=0
        for k in myOdb.steps.keys(): #��� ��� �����
            n=n+len(myOdb.steps[k].frames) #������� ������� ������ �� k ����� �������
            if k==step: res.append(x.data[n-1][1]) #������ �� ������ ����������
            #data �� ((���,��������),(���,��������)...)
    #�������� �������� ���
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #�������� ������ �������

def readODB_set_(set,var):
    '''������� ������ ���������� � ������ ������ �������
    (��� ������ fe-safe)
    set - �������
    var - �����:
    (('LOGLife-Repeats', ELEMENT_NODAL), )
    (('FOS@Life=Infinite', ELEMENT_NODAL), )
    (('%%Failure@Life=5E6-Repeats', ELEMENT_NODAL), )
    �������: readODB_set_(set='Set-1',var=var)
    '''
    #�������� ���
    dat=session.xyDataListFromField(odb=myOdb, outputPosition=NODAL, variable=var, nodeSets=(set.upper(),)) #���
    
    res=[] #������ ����������
    for x in dat: #��� ��� �����
        #x.data �� ((���,��������),(���,��������)...)
        res.append(x.data) #���
                            
    #�������� �������� ���
    for k in session.xyDataObjects.keys():
        del session.xyDataObjects[k] 
    return res #�������� ������ �������

def readODB_set2(set,step,var,pos=NODAL):
    '''���� ���������� � ���������� ������ ����� �� ������ ������
    (���� ����������� ������������ readODB_set())
    set - �������
    step - ����
    var - �����:
    ('S','Mises')
    ('S','Pressure')
    ('U','Magnitude')
    ('U','U1')
    ('CPRESS','')
    ('D','') #���������� ������ ������ ������
    pos - �������: NODAL - ��� �����,INTEGRATION_POINT - ��� ��������
    �������: readODB_set2(set='Cont',step='Step-1',var=('S','Mises'))
    '''
    if pos==NODAL:    
        s=myOdb.rootAssembly.nodeSets[set.upper()] #������� �����
    if pos==INTEGRATION_POINT:
        s=myOdb.rootAssembly.elementSets[set.upper()] #������� ��������
    if var[0]=='D': 
        fo=session.scratchOdbs['Model-1.odb'].steps['Session Step'].frames[-1].fieldOutputs['D'].getSubset(region=s,position=pos) #���
    else:
        fo=myOdb.steps[step].frames[-1].fieldOutputs[var[0]].getSubset(region=s,position=pos) #���
        #openOdb(r'C:/Temp/Model-1.odb').steps['Step-1'].frames[4].fieldOutputs['CPRESS'].getSubset(position=NODAL, region=openOdb(r'C:/Temp/Model-1.odb').rootAssembly.nodeSets['CONT']).values[0].data
    res=[] #������ ����������
    for v in fo.values: #��� ������� �����/��������
        if var[1]=='Mises': res.append(v.mises)#������ �� ������ ����������
        if var[1]=='Pressure': res.append(v.press)
        if var[0]=='U' and var[1]=='Magnitude': res.append(v.magnitude)
        if var[1]=='U1': res.append(v.data.tolist()[0])
        if var[1]=='U2': res.append(v.data.tolist()[1])
        if var[0]=='CPRESS': res.append(v.data)
        if var[0]=='D': res.append(v.data)
    return res #�������� ������ �������

def runFeSafe(input_odb,input_stlx,output_odb):
    '''������ ����� ������ ������ � fe-safe
    input_odb - ����� �������� ����� ���������� Abaqus (��� ���������� .odb)
    input_stlx - ����� ����� ����� fe-safe (��� ���������� .stlx)
    output_odb - ����� ��������� ����� ���������� Abaqus (��� ���������� .odb)
    ���� � FEA ����� ������������ ���������� � ����������, �� ����� ���������� ����� sltx � ������������� Analysis Options ��������� ������� Read strains from FE Models.
    '''
    s=r'd:\Program Files\Safe_Technology\fe-safe\version.6.2\exe\fe-safe_cl.exe -s j=c:\1\{iodb}.odb b=c:\1\{istlx}.stlx o=c:\1\{oodb}.odb'
    s=s.format(iodb=input_odb, istlx=input_stlx, oodb=output_odb)
    # ������ ���������� � fe-safe �� ���� ����������
    subprocess.Popen(s).communicate()
    
def writeLDFfile(filename,lst):
    '''����� ���� ����� ���������� ������������ LDF fe-safe
    filename - ��� �����
    lst - ������ �����-�����
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

""" # ������ �����
    s=s.format(x=lst[0]) # ���� ����� � �������
    f.write(s)
    f.close()
    
def SF_field(s1='Step-1',s2='Step-2',Sn=207000000,m=1):
    '''��������� ���� ����������� ������ ������ ������ �� ������� ������''' 
        
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
    shutil.copyfile(model.name + '.odb', 'MyDB/'+name+'.odb')#�������� ����
    
    my_db = shelve.open("MyDB/mydb")#������� ���� ������
    my_db[name]=[mat1,mat2,d,d_n]#�������� � ������ �� ������ name
    my_db.close()#������� ���� ������
def readDB(name):
    import shelve
    my_db = shelve.open("MyDB/mydb")#������� ���� ������
    print my_db.keys()#������� ������ ��� ������
    if my_db.has_key(name):#���� � ���� name
        print my_db[name]
    my_db.close()#������� ���� ������
