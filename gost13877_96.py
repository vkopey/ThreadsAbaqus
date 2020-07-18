# -*- coding: cp1251 -*-
'''ìîäåëü ìóôòîâîãî ð³çüáîâîãî çºäíàííÿ íàñîñíèõ øòàíã (ÃÎÑÒ 13877-96)'''
if _my_thread_model!=1: from tools import *

rod19={'d_n':(27, -0.48, -0.376),#
    'd2_n':(25.35, -0.204, -0.047),#
    'd1_n':(24.25, 0, -0.415),
    'r_n':(0.28, 0, 0.08),
    'dn':(38.1, -0.25, 0.13),
    'd1n':(23.24, -0.13, 0.13),
    'l1n':(36.5, 0, 1.6),
    'l2n':(15, 0.2, 1),
    'l3n':(32, 0, 1.5),
    'l4n':(48, -1, 1.5),
    'r3n':(3, 0, 0.8),
    'd_m':(27, 0, 0.27),
    'd2_m':(25.35, 0, 0.202),
    'd1_m':(24.25, 0, 0.54),
    'dm':(41.3, -0.25, 0.13),
    'd1m':(27.43, 0, 0.25),
    'lm':(102, -1, 1),
    'd0':(19.1,-0.41,0.2),
    'p_n':(2.54,0,0),
    'p_m':(2.54,0,0)}
rod22={'d_n':(27, -0.48, -0.376),#
    'd2_n':(25.35, -0.204, -0.047),#
    'd1_n':(24.25, 0, -0.415),
    'r_n':(0.28, 0, 0.08),
    'dn':(38.1, -0.25, 0.13),
    'd1n':(23.24, -0.13, 0.13),
    'l1n':(36.5, 0, 1.6),
    'l2n':(15, 0.2, 1),
    'l3n':(32, 0, 1.5),
    'l4n':(48, -1, 1.5),
    'r3n':(3, 0, 0.8),
    'd_m':(27, 0, 0.27),
    'd2_m':(25.35, 0, 0.202),
    'd1_m':(24.25, 0, 0.54),
    'dm':(41.3, -0.25, 0.13),
    'd1m':(27.43, 0, 0.25),
    'lm':(102, -1, 1),
    'd0':(19.1,-0.41,0.2),
    'p_n':(2.54,0,0),
    'p_m':(2.54,0,0)}

rod={19:rod19,22:rod22}#ñëîâíèê òèïîðîçì³ð³â øòàíã
diameter=19#ä³àìåòð øòàíãè
d={}#ñëîâíèê óñ³õ ðîçì³ð³â ìîäåë³
for x in rod[diameter].iterkeys():
    d[x]=Dim(rod[diameter][x])#êîï³þºìî êëþ÷³, à çíà÷åííÿ ïåðåòâîðþºìî â ðîçì³ðè Dim

l_=0#ñêîðî÷åííÿ ìóôòè ïðè çãâèí÷óâàíí³ (0, ÿêùî çàäàíî Bolt Load)
#=====================ïàðàìåòðè í³ïåëÿ øòàíãè===================
d['d_n'] = d['d_n'].min() / 2 #çîâí³øí³é ä³àìåòð ð³çüáè/2
d['d2_n'] = d['d2_n'].min() / 2 #ñåðåäí³é ä³àìåòð ð³çüáè/2
d['d1_n'] = d['d1_n'].min() / 2 #âíóòð³øí³é ä³àìåòð ð³çüáè/2!ei*
d['r_n'] = d['r_n'].min() #ðàä³óñ çàïàäèí ð³çüáè
d['p_n'] = d['p_n'].min() #êðîê ð³çüáè
d['dn'] = d['dn'].min() / 2 #ä³àìåòð áóðòà/2
d['d1n'] = d['d1n'].min() / 2 #ä³àìåòð çàð³çüáîâî¿ êàíàâêè/2
d['l1n'] = d['l1n'].min()+my_iter2 #äîâæèíà í³ïåëÿ
d['l2n'] = d['l2n'].min()+my_iter2 #äîâæèíà çàð³çüáîâî¿ êàíàâêè
d['l3n'] = d['l3n'].min()+my_iter2 #äîâæèíà í³ïåëÿ áåç ôàñêè íà ð³çüá³
d['l4n'] = d['l4n'].min()+my_iter2 #äîâæèíà í³ïåëÿ ç áóðòîì
d['r3n'] = d['r3n'].min() #ðàä³óñ ñêðóãëåíü çàð³çüáîâî¿ êàíàâêè
d['d0']=d['d0'].min()/2 #ä³àìåòð ò³ëà/2
#=====================ïàðàìåòðè ìóôòè===========================
d['d_m'] = d['d_m'].max() / 2 #çîâí³øí³é ä³àìåòð ð³çüáè/2!es*
d['d2_m'] = d['d2_m'].max() / 2 #ñåðåäí³é ä³àìåòð ð³çüáè/2
d['d1_m'] = d['d1_m'].max() / 2 #âíóòð³øí³é ä³àìåòð ð³çüáè/2
d['p_m'] = d['p_m'].min() #êðîê ð³çüáè
d['dm'] = d['dm'].min() / 2 #çîâí³øí³é ä³àìåòð/2
d['d1m'] = d['d1m'].max() / 2 #âíóòð³øí³é ä³àìåòð îïîðíî¿ ïîâåðõí³/2
d['lm'] = d['lm'].min() / 2 +my_iter2#äîâæèíà ìóôòè/2
#================äîïîì³æí³ ïàðàìåòðè========================
d['dn_']=d['d2_n']+0.25*d['p_n']/tan(30*pi/180)#çîâí³øí³é ä³àìåòð âåðøèí òðèêóòíèêà ïðîô³ëÿ í³ïåëÿ
d['ln_']=d['l1n']-d['l2n']#z-êîîðäèíàòà ïåðøî¿ çàïàäèíè í³ïåëÿ (äîâæèíà ð³çüáè í³ïåëÿ)
d['dm_']=d['d2_m']-0.25*d['p_m']/tan(30*pi/180)#âíóòð³øí³é ä³àìåòð âåðøèí òðèêóòíèêà ïðîô³ëÿ ìóôòè
d['lm_']=d['lm']-11.1#äîâæèíà ð³çüáè ìóôòè
d['l2m_']=d['ln_']+ceil((d['l2n']-11.1)/d['p_m'])*d['p_m']-3*d['p_m']/2-(d['d2_m']-d['d2_n'])*tan(30*pi/180)#z-êîîðäèíàòà ïåðøî¿ çàïàäèíè ìóôòè
#ceil((d['l2n']-11.1)/d['p_m'])*d['p_m'] - ïåðø³ íåðîáî÷³ âèòêè ìóôòè
#-3*d['p_m']/2-(d['d2_m']-d['d2_n'])*tan(30*pi/180) - çì³ùåííÿ ïðîô³ëþ ìóôòè
#================òî÷êè õàðàêòåðíèõ êðîìîê ìîäåë³========================
en1=(d['dn']/2, d['l1n']+20, 0.0)#âåðõí³é òîðåöü øòàíãè
en2=(0.0, (d['l1n']+20)/2, 0.0)#â³ñü í³ïåëÿ
en3=(d['d1_n']/2,0.0,0.0)#íèæí³é òîðåöü øòàíãè
en4=(d['dn'],d['l1n']+10,0.0)#çîâí³øí³é öèë³íäð áóðòà
enr1=(d['d2_n']-0.25*d['p_n']/tan(30*pi/180)+d['r_n']/sin(30*pi/180)-d['r_n'],d['ln_'],0.0)#öåíòð ïåðøî¿ çàïàäèíè í³ïåëÿ
em1=((d['dm']+d['d_m'])/2, d['l1n']-d['lm']+l_, 0.0)#íèæí³é òîðåöü ìóôòè (çì³ùåííÿ +l_)
em2=(d['dm'],d['l1n']/2,0.0)#çîâí³øí³é öèë³íäð ìóôòè
em3=((d['dm']+d['d1m'])/2,d['l1n']-5,0.)#öåíòð Partition face-1 (äëÿ Bolt Load)
em4=((d['dm']+d['d1m'])/2,d['l1n'],0.)#âåðõí³é òîðåöü ìóôòè
nn=8#ê³ëüê³ñòü çàïàäèí í³ïåëÿ äëÿ äîñë³äæåííÿ
#mat1=matlib['40'].power(8) # ìàòåð³àë 1
#mat2=matlib['40'].power(8) # ìàòåð³àë 2
mat1=matlib['40fesafe'].bilinear() # ìàòåð³àë 1
mat2=matlib['40fesafe'].bilinear() # ìàòåð³àë 2
bolt_load=-my_iter1 #-0.1
load1=-1*d['d0']**2/d['dn']**2
load2=-170.0e+6*d['d0']**2/d['dn']**2

def createSketch1():
    "Ñòâîðþº åñê³ç ïðîô³ëþ ð³çüáè í³ïåëÿ"
    s=model.ConstrainedSketch(name='Sketch-1', sheetSize=200.0)
    #Ãåîìåòð³ÿ
    g1=s.ConstructionLine(angle=0.0, point1=(0.0, 0.0))
    s.HorizontalConstraint(entity=g1)
    s.FixedConstraint(entity=g1)
    g2=s.Line(point1=(0.0, -15.0), point2=(0.0, 15.0))
    s.VerticalConstraint(entity=g2)
    g3=s.Line(point1=(0.0, 15.0), point2=(-20.0, 5.0))
    g4=s.Line(point1=(0.0, -15.0), point2=(-20.0, -5.0))
    g5=s.ArcByStartEndTangent(entity=g3, point1=(-20.0, 5.0), point2=(-20.0, -5.0))
    s.TangentConstraint(entity1=g4, entity2=g5)
    s.CoincidentConstraint(entity1=g5.getVertices()[2], entity2=g1)
    #Ðîçì³ðè ³ ïàðàìåòðè
    d1=s.VerticalDimension(vertex1=g2.getVertices()[0], vertex2=g2.getVertices()[1],textPoint=(0.0, 0.0))
    s.Parameter(name='p_n', path='dimensions[0]')
    d2=s.AngularDimension(line1=g1, line2=g3, textPoint=(10.0, 10.0))
    s.Parameter(name='alf1', path='dimensions[1]')
    d3=s.AngularDimension(line1=g1, line2=g4, textPoint=(10.0, -10.0))
    s.Parameter(name='alf2', path='dimensions[2]')
    d4=s.RadialDimension(curve=g5, textPoint=(0.0, 0.0))
    s.Parameter(name='r_n', path='dimensions[3]')
def createSketch2():
    "Ñòâîðþº åñê³ç ïðîô³ëþ ð³çüáè ìóôòè"
    s=model.ConstrainedSketch(name='Sketch-2', sheetSize=200.0)
    #Ãåîìåòð³ÿ
    g1=s.ConstructionLine(angle=0.0,point1=(0.0, 0.0))
    s.HorizontalConstraint(entity=g1)
    s.FixedConstraint(entity=g1)
    g2=s.Line(point1=(0.0, 0.0), point2=(0.0, 20.0))
    s.VerticalConstraint(entity=g2)
    s.PerpendicularConstraint(entity1=g1, entity2=g2)
    s.CoincidentConstraint(entity1=g2.getVertices()[0], entity2=g1)
    g3=s.Line(point1=(0.0, 0.0), point2=(0.0, -20.0))
    s.VerticalConstraint(entity=g3)
    s.ParallelConstraint(entity1=g2, entity2=g3)
    s.EqualLengthConstraint(entity1=g2, entity2=g3)
    g4=s.Line(point1=(0.0, -20.0), point2=(25.0, -5.0))
    g5=s.Line(point1=(25.0, -5.0), point2=(25.0, 5.0))
    s.VerticalConstraint(entity=g5)
    g6=s.Line(point1=(25.0, 5.0), point2=(0.0, 20.0))
    #Ðîçì³ðè ³ ïàðàìåòðè
    d1=s.VerticalDimension(vertex1=g2.getVertices()[1], vertex2=g3.getVertices()[1],textPoint=(0.0, 0.0))
    s.Parameter(name='p_m', path='dimensions[0]')
    d2=s.AngularDimension(line1=g1, line2=g6, textPoint=(-10.0, 10.0))
    s.Parameter(name='alf1', path='dimensions[1]')
    d3=s.AngularDimension(line1=g1, line2=g4, textPoint=(-10.0, -10.0))
    s.Parameter(name='alf2', path='dimensions[2]')
    d4=s.DistanceDimension(entity1=g2, entity2=g5, textPoint=(0.0, 0.0))
    s.Parameter(name='h', path='dimensions[3]')
def createSketch3():
    "Ñòâîðþº åñê³ç çàãîòîâêè í³ïåëÿ"
    s=model.ConstrainedSketch(name='Sketch-3', sheetSize=200.0)
    #Ãåîìåòð³ÿ
    g1=s.Line(point1=(0.0, 0.0), point2=(0.0, 50.0))
    s.VerticalConstraint(entity=g1)
    s.FixedConstraint(entity=g1.getVertices()[0])
    g2=s.Line(point1=(0.0, 50.0), point2=(20.0, 50.0))
    s.HorizontalConstraint(entity=g2)
    g3=s.Line(point1=(20.0, 50.0), point2=(20.0, 40.0))
    s.VerticalConstraint(entity=g3)
    g4=s.Line(point1=(20.0, 40.0), point2=(10.0, 40.0))
    s.HorizontalConstraint(entity=g4)
    g5=s.ArcByStartEndTangent(entity=g4, point1=(10.0, 40.0), point2=(5.0, 35.0))
    g6=s.Line(point1=(5.0, 35.0), point2=(5.0, 30.0))
    s.VerticalConstraint(entity=g6)
    s.TangentConstraint(entity1=g5, entity2=g6)
    g7=s.ArcByStartEndTangent(entity=g6, point1=(5.0, 30.0), point2=(10.0, 25.0))
    g8=s.Line(point1=(10.0, 25.0), point2=(10.0, 5.0))
    s.VerticalConstraint(entity=g8)
    g9=s.Line(point1=(10.0, 5.0), point2=(5.0, 0.0))
    g10=s.Line(point1=(5.0, 0.0), point2=(0.0, 0.0))
    s.HorizontalConstraint(entity=g10)
    #Ðîçì³ðè ³ ïàðàìåòðè
    d1=s.DistanceDimension(entity1=g2, entity2=g10, textPoint=(0.0, 0.0))
    s.Parameter(name='ln', path='dimensions[0]')
    d2=s.DistanceDimension(entity1=g1, entity2=g3, textPoint=(0.0, 0.0))
    s.Parameter(name='dn', path='dimensions[1]')
    d3=s.DistanceDimension(entity1=g1, entity2=g8, textPoint=(0.0, 0.0))
    s.Parameter(name='d_n', path='dimensions[2]')
    d4=s.DistanceDimension(entity1=g1, entity2=g6, textPoint=(0.0, 0.0))
    s.Parameter(name='d1n', path='dimensions[3]')
    d5=s.DistanceDimension(entity1=g4, entity2=g10, textPoint=(0.0, 0.0))
    s.Parameter(name='l1n', path='dimensions[4]')
    d6=s.DistanceDimension(entity1=g4, entity2=g8.getVertices()[0], textPoint=(0.0, 0.0))
    s.Parameter(name='l2n', path='dimensions[5]')
    d7=s.DistanceDimension(entity1=g4, entity2=g8.getVertices()[1], textPoint=(0.0, 0.0))
    s.Parameter(name='l3n', path='dimensions[6]')
    d8=s.AngularDimension(line1=g9, line2=g1, textPoint=(10.0, 10.0))
    s.Parameter(name='fn', path='dimensions[7]')
    d9=s.RadialDimension(curve=g5, textPoint=(0.0, 0.0))
    s.Parameter(name='r3n1', path='dimensions[8]')
    d10=s.RadialDimension(curve=g7, textPoint=(0.0, 0.0))
    s.Parameter(name='r3n2', path='dimensions[9]')
    s.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
def createSketch4():
    "Ñòâîðþº åñê³ç çàãîòîâêè ìóôòè"
    s=model.ConstrainedSketch(name='Sketch-4', sheetSize=200.0)
    #Ãåîìåòð³ÿ
    v1=s.Spot(point=(0.0, 0.0))
    s.FixedConstraint(entity=v1)
    g1=s.Line(point1=(10.0, -10.0), point2=(10.0, 20.0))
    s.VerticalConstraint(entity=g1)
    g2=s.Line(point1=(10.0, 20.0), point2=(15.0, 25.0))
    g3=s.Line(point1=(15.0, 25.0), point2=(15.0, 35.0))
    s.VerticalConstraint(entity=g3)
    g4=s.Line(point1=(15.0, 35.0), point2=(20.0, 40.0))
    g5=s.Line(point1=(20.0, 40.0), point2=(25.0, 40.0))
    s.HorizontalConstraint(entity=g5)
    g6=s.Line(point1=(25.0, 40.0), point2=(30.0, 35.0))
    g7=s.Line(point1=(30.0, 35.0), point2=(30.0, -10.0))
    s.VerticalConstraint(entity=g7)
    g8=s.Line(point1=(30.0, -10.0), point2=(10.0, -10.0))
    s.HorizontalConstraint(entity=g8)
    #Ðîçì³ðè ³ ïàðàìåòðè
    d1=s.DistanceDimension(entity1=g5, entity2=v1, textPoint=(0.0, 0.0))
    s.Parameter(name='l1n', path='dimensions[0]')
    d2=s.DistanceDimension(entity1=g5, entity2=g2.getVertices()[1], textPoint=(0.0, 0.0))
    s.Parameter(name='l1m', path='dimensions[1]')
    d3=s.DistanceDimension(entity1=g5, entity2=g3.getVertices()[1], textPoint=(0.0, 0.0))
    s.Parameter(name='lf1m', path='dimensions[2]')
    d4=s.DistanceDimension(entity1=g5, entity2=g6.getVertices()[1], textPoint=(0.0, 0.0))
    s.Parameter(name='lf2m', path='dimensions[3]')
    d5=s.DistanceDimension(entity1=g5, entity2=g8, textPoint=(0.0, 0.0))
    s.Parameter(name='lm', path='dimensions[4]')
    d6=s.DistanceDimension(entity1=g1, entity2=v1, textPoint=(0.0, 0.0))
    s.Parameter(name='d1_m', path='dimensions[5]')
    d7=s.DistanceDimension(entity1=g3, entity2=v1, textPoint=(0.0, 0.0))
    s.Parameter(name='d1m', path='dimensions[6]')
    d8=s.DistanceDimension(entity1=g7, entity2=v1, textPoint=(0.0, 0.0))
    s.Parameter(name='dm', path='dimensions[7]')
    d9=s.AngularDimension(line1=g1, line2=g2, textPoint=(10.0, 10.0))
    s.Parameter(name='f_m', path='dimensions[8]')
    d10=s.AngularDimension(line1=g3, line2=g4, textPoint=(10.0, 10.0))
    s.Parameter(name='f1m', path='dimensions[9]')
    d11=s.AngularDimension(line1=g6, line2=g7, textPoint=(50.0, -50.0))
    s.Parameter(name='f2m', path='dimensions[10]')
    s.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
def create_nipple2():
    par={'aint':0,'aext':0,'Rint':0,'Rext':d['dn'],'len':d['l1n']+20}
    set_values2(sketch='nipple',base='Quad_h',p=par)
    p=model.Part(dimensionality=AXISYMMETRIC, name='Part-1', type=DEFORMABLE_BODY)
    p.BaseShell(sketch=model.sketches['nipple'])
    del model.sketches['nipple']
    
    par={'aint':0,'aext':0,'Rint':d['d1n'],'Rext':d['dn'],'len':d['l2n'],'Ra':d['r3n'],'Rb':d['r3n']}
    set_values2(sketch='groove',base='Quad_h_fillet_int',p=par)
    part_builder(p, 'groove', (0,d['l1n']-d['l2n']), 'cut')
    del model.sketches['groove']
    
    par={'aint':0,'aext':0,'Rint':d['d_n'],'Rext':d['dn'],'len':d['l1n']-d['l2n']/2}
    set_values2(sketch='cut_nipple',base='Quad_h',p=par)
    part_builder(p, 'cut_nipple', (0,0), 'cut')
    del model.sketches['cut_nipple']
    
    par={'aa':30,'ab':90,'h':d['l1n']-d['l3n']}
    set_values2(sketch='chamfer',base='Triangle_v_int',p=par)
    part_builder(p, 'chamfer', (d['d_n'],0), 'cut')
    del model.sketches['chamfer']
    
    par={'aa':60,'ab':60,'len':d['p_n'],'R':d['r_n']}
    set_values2(sketch='thread',base='Triangle_v_fillet_int',p=par)
    i=0 #íîìåð âèòêà (0-ïåðøèé)
    while i*d['p_n']<=d['ln_']:#äîâæèíà ð³çüáè
        part_builder(p, 'thread', (d['dn_'],d['ln_']-d['p_n']*i), 'cut')
        i+=1
    del model.sketches['thread']
def create_coupling2():
    par={'aint':0,'aext':0,'Rint':d['d1_m'],'Rext':d['dm'],'len':d['l1n']-11.1}
    set_values2(sketch='coupling',base='Quad_h',p=par)
    p=model.Part(dimensionality=AXISYMMETRIC, name='Part-2', type=DEFORMABLE_BODY)
    p.BaseShell(sketch=model.sketches['coupling'])
    del model.sketches['coupling']
    
    par={'aint':0,'aext':0,'Rint':d['d1_m'],'Rext':d['dm'],'len':d['lm']-d['l1n']}
    set_values2(sketch='coupling_bot',base='Quad_h',p=par)
    part_builder(p, 'coupling_bot', (0,-(d['lm']-d['l1n'])), 'shell')
    del model.sketches['coupling_bot']
    
    par={'aint':0,'aext':0,'Rint':d['d1m'],'Rext':d['dm'],'len':11.1}
    set_values2(sketch='coupling_top',base='Quad_h',p=par)
    part_builder(p, 'coupling_top', (0,d['l1n']-11.1), 'shell')
    del model.sketches['coupling_top']
    
    #par={'aa':90,'ab':30,'t':d['d1m']-d['d1_m']}
    s=model.ConstrainedSketch(name='Sketch-1', sheetSize=200.0)
    s.Line(point1=(0.0, d['l1n']-11.1), point2=(d['d1m'], d['l1n']-11.1))
    s.Line(point1=(0.0, d['l1n']-11.1), point2=(0.0, (d['l1n']-11.1)-d['d1m']/tan(radians(30))))
    s.Line(point1=(d['d1m'], d['l1n']-11.1), point2=(0.0, (d['l1n']-11.1)-d['d1m']/tan(radians(30))))
    #ñòâîðèòè êëàñ
    #set_values2(sketch='chamfer',base='Sketch-1',p=par)
    part_builder(p, 'Sketch-1', (0,0), 'cut')
    del model.sketches['Sketch-1']
    
    par={'aa':90,'ab':30,'h':2}
    set_values2(sketch='chamfer',base='Triangle_v_ext',p=par)
    part_builder(p, 'chamfer', (d['d1m'],d['l1n']-2), 'cut')
    del model.sketches['chamfer']
    
    par={'aa':90,'ab':15,'h':3}
    set_values2(sketch='chamfer',base='Triangle_v_int',p=par)
    part_builder(p, 'chamfer', (d['dm'],d['l1n']-3), 'cut')
    del model.sketches['chamfer']
    
    par={'aa':120,'ab':120,'h':d['p_m'],'t':2.2-0.275}
    set_values2(sketch='thread',base='Quad_v',p=par)
    i=0
    while i*d['p_m']<=d['lm_']-3*d['p_m']/2:#äîâæèíà ð³çüáè-3*d['p_m']/2
        part_builder(p, 'thread', (d['dm_'],d['l2m_']-d['p_m']*i), 'cut')
        i+=1
    del model.sketches['thread']

def create_nipple3():
    s=model.ConstrainedSketch(name='nipple', sheetSize=200.0)
    L1=Line(p1=(0,0),len=d['l1n']+20,angle=90)
    L2=Line(p1=L1.p1,len=d['dn'],angle=0)
    L3=Line(p1=L2.p2,len=d['l1n']+20,angle=90)
    L4=Line(p1=L3.p2,p2=L1.p2)
    N_angle([L1,L2,L3,L4], [0,0,0,0]).drawAbaqus(s)
    del L1,L2,L3,L4
    s.ConstructionLine(point1=(0.0, 0.0), angle=90.0) 
    p=model.Part(dimensionality=AXISYMMETRIC, name='Part-1', type=DEFORMABLE_BODY)
    p.BaseShell(sketch=model.sketches['nipple'])
    del s
    
    s=model.ConstrainedSketch(name='groove', sheetSize=200.0)
    L1=Line(p1=(d['dn'],d['l1n']-d['l2n']),len=d['l2n'],angle=90)
    L2=Line(p1=L1.p2,len=d['dn']-d['d1n'],angle=180)
    L3=Line(p1=L2.p2,len=d['l2n'],angle=360-90)
    L4=Line(p1=L3.p2,p2=L1.p1)
    N_angle([L1,L2,L3,L4], [0,d['r3n'],d['r3n'],0]).drawAbaqus(s)
    del L1,L2,L3,L4
    part_builder(p, 'groove', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='cut_nipple', sheetSize=200.0)
    L1=Line(p1=(d['d_n'],0),len=d['l1n']-d['l2n']/2,angle=90)
    L2=Line(p1=L1.p2,len=d['dn']-d['d_n'],angle=0)
    L3=Line(p1=L2.p2,len=d['l1n']-d['l2n']/2,angle=360-90)
    L4=Line(p1=L3.p2,p2=L1.p1)
    N_angle([L1,L2,L3,L4], [0,0,0,0]).drawAbaqus(s)
    del L1,L2,L3,L4
    part_builder(p, 'cut_nipple', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='chamfer', sheetSize=200.0)
    L1=Line(p1=(d['d_n'],0),len=d['l1n']-d['l3n'],angle=90)
    cp=Line(p1=L1.p1,angle=180).cros_point(Line(p1=L1.p2,angle=180+60))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    N_angle([L1,L2,L3], [0,0,0]).drawAbaqus(s)
    del L1,L2,L3,cp
    part_builder(p, 'chamfer', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='thread', sheetSize=200.0)
    L1=Line(p1=(d['dn_'],0),len=d['p_n'],angle=90)
    cp=Line(p1=L1.p1,angle=90+60).cros_point(Line(p1=L1.p2,angle=270-60))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    N_angle([L1,L2,L3], [0,d['r_n'],0]).drawAbaqus(s)
    del L1,L2,L3,cp
    i=0 #íîìåð âèòêà (0-ïåðøèé)
    while i*d['p_n']<=d['ln_']:#äîâæèíà ð³çüáè
        part_builder(p, 'thread', (0,d['ln_']-d['p_n']*i), 'cut')
        i+=1
    del s     

def create_coupling3():
    s=model.ConstrainedSketch(name='coupling', sheetSize=200.0)
    L1=Line(p1=(d['dm'],-(d['lm']-d['l1n'])),len=d['lm']-11.1,angle=90)
    L2=Line(p1=L1.p2,len=d['dm']-d['d1_m'],angle=180)
    L3=Line(p1=L2.p2,len=d['lm']-11.1,angle=270)
    L4=Line(p1=L3.p2,p2=L1.p1)
    N_angle([L1,L2,L3,L4], [0,0,0,0]).drawAbaqus(s)
    del L1,L2,L3,L4
    s.ConstructionLine(point1=(0.0, 0.0), angle=90.0) 
    p=model.Part(dimensionality=AXISYMMETRIC, name='Part-2', type=DEFORMABLE_BODY)
    p.BaseShell(sketch=model.sketches['coupling'])
    del s
    
    s=model.ConstrainedSketch(name='top', sheetSize=200.0)
    L1=Line(p1=(d['dm'],d['l1n']-11.1),len=11.1,angle=90)
    L2=Line(p1=L1.p2,len=d['dm']-d['d1m'],angle=180)
    L3=Line(p1=L2.p2,len=11.1,angle=270)
    L4=Line(p1=L3.p2,p2=L1.p1)
    N_angle([L1,L2,L3,L4], [0,0,0,0]).drawAbaqus(s)
    del L1,L2,L3,L4
    part_builder(p, 'top', (0,0), 'shell')
    del s
    
    s=model.ConstrainedSketch(name='chamfer', sheetSize=200.0)
    L1=Line(p1=(d['d1m'],d['l1n']-11.1),len=d['d1m']-d['d1_m'],angle=180)
    cp=Line(p1=L1.p1,angle=180+60).cros_point(Line(p1=L1.p2,angle=270))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    N_angle([L1,L2,L3], [0,0,0]).drawAbaqus(s)
    del L1,L2,L3,cp
    part_builder(p, 'chamfer', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='chamfer', sheetSize=200.0)
    L1=Line(p1=(d['d1m'],d['l1n']),len=2.0,angle=270)
    cp=Line(p1=L1.p1,angle=0).cros_point(Line(p1=L1.p2,angle=90-30))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    N_angle([L1,L2,L3], [0,0,0]).drawAbaqus(s)
    del L1,L2,L3,cp
    part_builder(p, 'chamfer', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='chamfer', sheetSize=200.0)
    L1=Line(p1=(d['dm'],d['l1n']),len=3.0,angle=270)
    cp=Line(p1=L1.p1,angle=180).cros_point(Line(p1=L1.p2,angle=90+15))
    L2=Line(p1=L1.p1,p2=cp)
    L3=Line(p1=L1.p2,p2=cp)
    N_angle([L1,L2,L3], [0,0,0]).drawAbaqus(s)
    del L1,L2,L3,cp
    part_builder(p, 'chamfer', (0,0), 'cut')
    del s
    
    s=model.ConstrainedSketch(name='thread', sheetSize=200.0)
    L1=Line(p1=(d['dm_'],0),len=d['p_m'],angle=90)
    cp1=Line(p1=L1.p1,angle=90-60).cros_point(Line(p1=(d['dm_']+1.93,0),angle=90))
    L2=Line(p1=L1.p1,p2=cp1)
    cp2=Line(p1=L1.p2,angle=270+60).cros_point(Line(p1=cp1,angle=90))
    L3=Line(p1=cp1,p2=cp2)
    L4=Line(p1=L1.p2,p2=cp2)
    N_angle([L1,L2,L3,L4], [0,0,0,0]).drawAbaqus(s)
    del L1,L2,L3,L4,cp1,cp2
    i=0
    while i*d['p_m']<=d['lm_']-3*d['p_m']/2:#äîâæèíà ð³çüáè-3*d['p_m']/2
        part_builder(p, 'thread', (0,d['l2m_']-d['p_m']*i), 'cut')
        i+=1
    del s                  
def createProfile():
    "Ñòâîðþº ïðîô³ëü ð³çüáè í³ïåëÿ ³ ìóôòè"
    delCutExtrude()
    #ñòâîðåííÿ ïðîô³ëþ ð³çüáè í³ïåëÿ
    #ìîæíà öå çðîáèòè òàêîæ çà äîïîìîãîþ LinearInstancePattern
    i=0 #íîìåð âèòêà (0-ïåðøèé)
    while i*d['p_n']<=d['ln_']:#äîâæèíà ð³çüáè
     s=model.ConstrainedSketch(name='__profile__',sheetSize=200.)
     #s.sketchOptions.setValues(viewStyle=AXISYM)
     model.parts['Part-1'].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=s)
     s.ConstructionLine(point1=(0.0,0.0), point2=(0.0, 10.0))
     s.retrieveSketch(sketch=model.sketches['Sketch-1'])
     s.move(objectList=s.geometry.values(),vector=(d['dn_'],d['ln_']-d['p_n']*i))
     model.parts['Part-1'].Cut(sketch=s)
     del s
     i=i+1
    #ñòâîðåííÿ ïðîô³ëþ ð³çüáè ìóôòè
    i=0
    while i*d['p_m']<=d['lm_']-3*d['p_m']/2:#äîâæèíà ð³çüáè-3*d['p_m']/2
     s=model.ConstrainedSketch(name='__profile__',sheetSize=200.)
     #s.sketchOptions.setValues(viewStyle=AXISYM)
     model.parts['Part-2'].projectReferencesOntoSketch(filter=COPLANAR_EDGES, sketch=s)
     s.ConstructionLine(point1=(0.0,0.0), point2=(0.0, 10.0))
     s.retrieveSketch(sketch=model.sketches['Sketch-2'])
     s.move(objectList=s.geometry.values(),vector=(d['dm_'],d['l2m_']-d['p_m']*i))
     model.parts['Part-2'].Cut(sketch=s)
     del s
     i=i+1
     
def create_nipple_coupling():
    '''Ñïîñ³á ïîáóäîâè ãåîìåòð³¿ çà åñê³çàìè çàãîòîâîê äåòàëåé'''
    createSketch1()
    createSketch2()
    createSketch3()
    createSketch4()
    #ïàðàìåòðè ïðîô³ëþ ð³çüáè í³ïåëÿ
    par={'p_n':d['p_n'],'alf1':30,'alf2':30,'r_n':d['r_n']}
    set_values(sketch='Sketch-1',p=par)
    #ïàðàìåòðè ïðîô³ëþ ð³çüáè ìóôòè
    par={'p_m':d['p_m'],'alf1':30,'alf2':30,'h':2.2-0.275}
    set_values(sketch='Sketch-2',p=par)
    #ïàðàìåòðè çàãîòîâêè í³ïåëÿ
    par={'ln':d['l1n']+20,'d_n':d['d_n'],'dn':d['dn'],'d1n':d['d1n'],'l1n':d['l1n'],
         'l2n':d['l2n'],'l3n':d['l3n'],'r3n1':d['r3n'],'r3n2':d['r3n'],'fn':30}
    set_values(sketch='Sketch-3',p=par)
    #ïàðàìåòðè çàãîòîâêè ìóôòè
    par={'dm':d['dm'],'d1m':d['d1m'],'d1_m':d['d1_m'],'lm':d['lm'],'l1n':d['l1n']+l_,
         'lf1m':2,'lf2m':3,'f1m':30,'f2m':15,'f_m':30,'l1m':11.1}
    set_values(sketch='Sketch-4',p=par)
    createPart(n='Part-1',s='Sketch-3')
    createPart(n='Part-2',s='Sketch-4')
    createProfile()
def create_nipple_coupling2():
    '''Ñïîñ³á ïîáóäîâè ãåîìåòð³¿ çà ãîòîâèìè ïðîñòèìè åñê³çàìè'''
    create_nipple2()
    create_coupling2()
def create_nipple_coupling3():
    '''Ñïîñ³á ïîáóäîâè ãåîìåòð³¿ çà ïðîñòèìè åñê³çàìè'''
    create_nipple3()
    create_coupling3()
    
create_nipple_coupling()
#create_nipple_coupling2()
#create_nipple_coupling3()
#createPart3D('Part-1','nipple','Part-3')
#createPart3D('Part-2','coupling','Part-4')
createPartition(part='Part-2',offset=em3[1])
#createPartition3D(part='Part-4',offset=em3[1])
# ³çîòðîïíå çì³öíåííÿ:
#createMaterial('Material-1',et=mat1['el'],pt=mat1['pl'])
#createMaterial('Material-2',et=mat2['el'],pt=mat2['pl'])
# ê³íåìàòè÷íå çì³öíåííÿ:
createMaterial('Material-1',et=mat1['el'],pt=mat1['pl'],kinematic=True)
createMaterial('Material-2',et=mat2['el'],pt=mat2['pl'],kinematic=True)
createSectionAssign(n='Section-1',m='Material-1',p='Part-1')
createSectionAssign(n='Section-2',m='Material-2',p='Part-2')
#createSectionAssign3D(n='Section-1',m='Material-1',p='Part-3')
#createSectionAssign3D(n='Section-2',m='Material-2',p='Part-4')
createAssemblyInstance(n='Part-1-1',p='Part-1')
createAssemblyInstance(n='Part-2-1',p='Part-2')
#createAssemblyInstance3D(n='Part-3-1',p='Part-3')
#createAssemblyInstance3D(n='Part-4-1',p='Part-4')
createStep(n='Step-1',pr='Initial')
createStep(n='Step-2',pr='Step-1')
createContactSet(n='Slave',i='Part-1-1',ep=((en1, ), (en2, ), (en3, ), (en4, ),))#ñòâîðþºìî íàá³ð êðîìîê êîíòàêòó äëÿ í³ïåëÿ
createContactSet(n='Master',i='Part-2-1',ep=((em1, ), (em2, ),(em3,),))#ñòâîðþºìî íàá³ð êðîìîê êîíòàêòó äëÿ ìóôòè
#createContactSet3D(n='Slave',i='Part-3-1',ep=((en1, ), (en3, ), (en4, ),))#ñòâîðþºìî íàá³ð êðîìîê êîíòàêòó äëÿ í³ïåëÿ
#createContactSet3D(n='Master',i='Part-4-1',ep=((em1, ), (em2, ),(em3,),))#ñòâîðþºìî íàá³ð êðîìîê êîíòàêòó äëÿ ìóôòè
createContactProperty()
createContact()
#createContact3D()
createBCSet(n='Pressure',i='Part-1-1',ep=(en1, ))#òèñê
createBCSet(n='Axis',i='Part-1-1',ep=(en2, ))#çàêð³ïëåííÿ
createBCSet(n='Encastre',i='Part-2-1',ep=(em1, ))#çàêð³ïëåííÿ
#createBCSet3D(n='Pressure',i='Part-3-1',ep=(en1, ))#òèñê
#createBCSet3D(n='Encastre',i='Part-4-1',ep=(em1, ))#çàêð³ïëåííÿ
createBC_Pressure([('Step-1',load1),('Step-2',load2)])
createBC_Axis()
createBC_Encastre()
createBC_BoltLoad('Part-2-1',em3,bolt_load)
#createBC_Pressure3D([('Step-1',-1.0),('Step-2',-276.0e+6*d['d0']/d['dn'])])
#createBC_Encastre3D()
#createBC_BoltLoad3D('Part-2-1',em3,-0.1)
createMesh()
#createMesh3D()
createEdgesSet(n='Cont',i='Part-2-1',p=((em4, ),) )
createEdgesSet(n='First',i='Part-1-1',p=((enr1, ),) )
createVerticesSet(n='Zero point',i='Part-1-1',p=(((0,0,0), ),) )
createJobSubmit()


def createResults():
    global myOdb
    myOdb = openOdb(path=model.name + '.odb')
    session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)
    SF_field()       
    cont_pres=readODB_set(set='Cont',step='Step-2',var=(('CPRESS', ELEMENT_NODAL), ),pos=NODAL)
    result1=sum(cont_pres)/len(cont_pres)
    result2=min(readODB_set2(set='First',step='',var=('D',''),pos=INTEGRATION_POINT))
    result3=max(readODB_set(set='First',step='Step-2',var=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ),pos=INTEGRATION_POINT))
    result4=readODB_path(path=((d['d1n'],  d['l1n']-d['l2n']/2, 0.0),),step='Step-1',var=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ),intersections=False)
    myOdb.close()
    
    # ðåçóëüòàòè ç fe-safe
    oodb='results' # íàçâà áàçè äàíèõ ðåçóëüòàò³â
    runFeSafe('Model-1','my',oodb) # âèêîíàòè fe-safe
    myOdb = openOdb(path=oodb + '.odb') #â³äêðèòè áàçó äàíèõ ðåçóëüòàò³â
    session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)
    
    #îòðèìàòè ëîãàðèôì äîâãîâ³÷íîñò³ ó ìíîæèí³ âóçë³â Set-1
    var=(('LOGLife-Repeats', ELEMENT_NODAL), )
    x1=readODB_set_(set='SLAVE',var=var)
    x1min = min([x[0][1] for x in x1]) # çíàéòè ì³í³ìàëüíå çíà÷åííÿ
    
    #îòðèìàòè â³äñîòîê â³äìîâ ó ìíîæèí³ âóçë³â Set-1
    var=(('%%Failure@Life=5E6-Repeats', ELEMENT_NODAL), )
    x3=readODB_set_(set='SLAVE',var=var)
    x3max = max([x[0][1] for x in x3]) # çíàéòè ìàêñèìàëüíå çíà÷åííÿ
    
    myOdb.close()
    writer.writerow([my_iter1,my_iter2,result1,result2,result3,result4,x1min,x3max])

createResults()

#saveDB('B')
#readDB('B')
