# -*- coding: cp1251 -*-
'''модель муфтового різьбового зєднання НКТ (ГОСТ 633-80)'''
if _my_thread_model!=3: from tools import *

nkt114={'D':(114.3,0.0,0.0),#зовнішній діаметр труби
    'd':(100.3,0.0,0.0),#внутрішній діаметр труби
    'Dm':(132.1,0.0,0.0),#зовнішній діаметр муфти
    'Lm':(156.0,0.0,0.0),#довжина муфти*
    'P':(3.175,0.0,0.0),#крок різьби паралельно осі різьби
    'dsr':(112.566,0.0,0.0),#середній діаметр різьби в основній площині
    'd1':(111.031,0.0,0.0),#зовнішній діаметр різьби в площині торця труби
    'd2':(107.411,0.0,0.0),#внутрішній діаметр різьби в площині торця труби
    'L':(65.0,-3.2,3.2),#загальна довжина різьби труби
    'l':(52.3,0.0,0.0),#довжина різьби труби до основної площини (з повним профілем)
    'l1':(10.0,0.0,0.0),#максимальна довжина збігу різьби труби
    'd3':(111.219,0.0,0.0),#внутрішній діаметр різьби в площині торця муфти
    'd0':(115.9,0.0,0.8),#діаметр циліндричної виточки муфти
    'l0':(9.5,-0.5,1.5),#глибина виточки муфти
    'A':(6.5,0.0,0.0),#натяг при згвинчуванні вручну
    'fi':(atan(1.0/32)*180/pi,0.0,0.0),#кут нахилу
    'H':(2.75,0.0,0.0),#висота вихідного профілю
    'h1':(1.81,-0.1,0.05),#висота профілю різьби
    'h':(1.734,0.0,0.0),#робоча висота профілю
    'alfa_2':(30.0,-1.0,1.0),#кут нахилу сторони профілю alfa/2
    'r':(0.508,0.0,0.045),#радіус заокруглення вершини профілю
    'r1':(0.432,-0.045,0.0)}#радіус заокруглення впадини профілю
nkt102={'D':(114.3,-0.9,0.9),
    'd':(100.3,0.0,0.0),
    'Dm':(132.1,0.0,0.0),
    'Lm':(156.0,0.0,0.0),
    'P':(3.175,0.0,0.0),
    'dsr':(112.566,0.0,0.0),
    'd1':(111.031,0.0,0.0),
    'd2':(107.411,0.0,0.0),
    'L':(65.0,-3.2,3.2),
    'l':(52.3,0.0,0.0),
    'l1':(10.0,0.0,0.0),
    'd3':(111.219,0.0,0.0),
    'd0':(115.9,0.0,0.8),
    'l0':(9.5,-0.5,1.5),
    'A':(6.5,0.0,0.0),
    'fi':(atan(0.0625/2)*180/pi,0.0,0.0),
    'H':(2.75,0.0,0.0),
    'h1':(1.81,-0.1,0.05),
    'h':(1.734,0.0,0.0),
    'alfa_2':(30.0,-1.0,1.0),
    'r':(0.508,0.0,0.045),
    'r1':(0.432,-0.045,0.0)}

nkt={114:nkt114,102:nkt102}#словник типорозмірів
diameter=114#типорозмір
d={}#словник усіх розмірів моделі
for x in nkt[diameter].iterkeys():
    d[x]=Dim(nkt[diameter][x])#копіюємо ключі, а значення перетворюємо в розміри Dim

d['D'].v=d['D'].n/2
d['d'].v=d['d'].max()/2
d['Dm'].v=d['Dm'].min()/2
d['Lm'].v=d['Lm'].n/2
d['P'].v=d['P'].n
d['dsr'].v=d['dsr'].n/2
d['d1'].v=d['d1'].n/2
d['d2'].v=d['d2'].n/2
d['L'].v=d['L'].min()
d['l'].v=d['l'].n
d['l1'].v=d['l1'].n
d['d3'].v=d['d3'].n/2
d['d0'].v=d['d0'].min()/2
d['l0'].v=d['l0'].max()
d['A'].v=d['A'].n
d['fi'].v=d['fi'].n
d['H'].v=d['H'].n
d['h1'].v=d['h1'].max()
d['h'].v=d['h'].n
d['alfa_2'].v=d['alfa_2'].n
d['r'].v=d['r'].max()
d['r1'].v=d['r1'].min()
#================точки характерних кромок моделі========================
en1=((d['D'].v+d['d'].v)/2,d['L'].v+20,0.0)#верхній торець ніпеля
en2=(d['d'].v,d['L'].v/2,0.0)#внутрішній циліндр ніпеля
en3=(d['D'].v,d['L'].v+20-5,0.0)#зовнішній циліндр ніпеля
em1=(d['Dm'].v-5,d['L'].v-d['A'].v-d['Lm'].v,0.0)#нижній торець муфти
em2=(d['Dm'].v,0.0,0.0)#зовнішній циліндр муфти
mat1=matlib['40'].power(8)#матеріал 1
mat2=matlib['40'].power(8)#матеріал 2
bolt_load=my_iter1
load1=-1
load2=-my_iter2*1e+6

def createProfile():
    '''Створює профіль різьби ніпеля і муфти'''
    #X,Y=const+-n*p
    #створення профілю різьби ніпеля
    x=model.sketches['Sketch-3'].parameters['x'].value#допоміжний параметр
    dsr=d['D'].v-x#середній діаметр в основній площині
    createCut(Part='Part-1',Sketch='Sketch-3',Begin=0,P=d['P'].v,Fi=d['fi'].v,Len=d['L'].v-12.7,X=dsr,Y=d['L'].v-12.7,dx=-1,dy=-1)
    #витки з зрізаними вершинами
    n=createCut(Part='Part-1',Sketch='Sketch-3',Begin=1,P=d['P'].v,Fi=d['fi'].v,Len=12.7-d['l1'].v,X=d['D'].v-x,Y=d['L'].v-12.7,dx=1,dy=1)
    #збіг різьби
    createCut(Part='Part-1',Sketch='Sketch-3',Begin=1,P=d['P'].v,Fi=10.0,Len=d['l1'].v,X=d['D'].v-x,Y=d['L'].v-12.7+n*d['P'].v,dx=1,dy=1)
    #12.7 - кратне усім стандартним крокам
    #d['D'].v-x - середній діаметр в основній площині
    #створення профіля різьби муфти
    x=model.sketches['Sketch-4'].parameters['x'].value#допоміжний параметр
    createCut(Part='Part-2',Sketch='Sketch-4',Begin=0,P=d['P'].v,Fi=d['fi'].v,Len=d['Lm'].v-4,X=dsr,Y=d['L'].v-12.7,dx=-1,dy=-1)
    #X=d['d3'].v+x,Y=d['L'].v-d['A'].v

#параметри заготовки ніпеля
par={'ln':d['L'].v+20,'D':d['D'].v,'d':d['d'].v,'d2':d['d2'].v,'l':d['L'].v-12.7,'fi':d['fi'].v}
set_values(sketch='Sketch-1',p=par)
#параметри заготовки муфти
par={'Dm':d['Dm'].v,'Lm':d['Lm'].v,'d3':d['d3'].v,'d0':d['d0'].v,
    'l0':d['l0'].v,'fi':d['fi'].v,'lA':d['L'].v-d['A'].v,'hk':d['h1'].v+0.5}
set_values(sketch='Sketch-2',p=par)
#параметри профілю різьби ніпеля
par={'fi':d['fi'].v,'P':d['P'].v,'r1':d['r1'].v,'r':d['r'].v}
set_values(sketch='Sketch-3',p=par)
#параметри профілю різьби муфти
par={'fi':d['fi'].v,'P':d['P'].v,'r1':d['r1'].v,'r':d['r'].v}
set_values(sketch='Sketch-4',p=par)

createPart(n='Part-1',s='Sketch-1')
createPart(n='Part-2',s='Sketch-2')
createProfile()
createMaterial('Material-1',et=mat1['el'],pt=mat1['pl'])
createMaterial('Material-2',et=mat2['el'],pt=mat2['pl'])
createSectionAssign(n='Section-1',m='Material-1',p='Part-1')
createSectionAssign(n='Section-2',m='Material-2',p='Part-2')
createAssemblyInstance(n='Part-1-1',p='Part-1')
createAssemblyInstance(n='Part-2-1',p='Part-2')
createStep(n='Step-1',pr='Initial')
createStep(n='Step-2',pr='Step-1')
createContactSet(n='Slave',i='Part-1-1',ep=((en1, ), (en2, ), (en3, ),))#створюємо набір кромок контакту для ніпеля
createContactSet(n='Master',i='Part-2-1',ep=((em1, ), (em2, ),))#створюємо набір кромок контакту для муфти
createContactProperty()
createContact()
createBCSet(n='Pressure',i='Part-1-1',ep=(en1, ))#тиск
createBCSet(n='Encastre',i='Part-2-1',ep=(em1, ))#закріплення
createBC_Pressure([('Step-1',load1),('Step-2',load2)])
createBC_Encastre()
createMesh()
model.rootAssembly.translate(instanceList=('Part-2-1', ),
    vector=(0.0, bolt_load*d['P'].v, 0.0))#моделювання згвинчування(0(вручну),1,2(станок))

work_list=range(13)#розглядаємо 13 витків ніпеля
n=0
#(56.2047863424959,45.1455709929578,0) - координати робочої сторони першого витка
for x in work_list: #створюємо Set для кожної робочої сторони витка
    x=(56.2047863424959-n*d['P'].v*tan(radians(d['fi'].v)), 45.1455709929578-n*d['P'].v, 0)
    createEdgesSet(n='work'+str(n),i='Part-1-1',p=((x, ),) )
    n+=1
n=0
nwork_list=range(13)#розглядаємо 13 витків ніпеля
for x in nwork_list: #створюємо Set для кожної неробочої сторони витка
    x=(56.1551769672515-n*d['P'].v*tan(radians(d['fi'].v)), 43.5580709924834-n*d['P'].v, 0)
    createEdgesSet(n='nwork'+str(n),i='Part-1-1',p=((x, ),) )
    n+=1

createJobSubmit()

myOdb = openOdb(path=model.name + '.odb')
def createResults():
    session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)    
    for x in range(13):
        cont_pres=readODB_set2(set='work'+str(x),step='Step-2',var=('CPRESS',''),pos=NODAL)
        result1=sum(cont_pres)/len(cont_pres)
        cont_pres=readODB_set2(set='nwork'+str(x),step='Step-2',var=('CPRESS',''),pos=NODAL)
        result2=sum(cont_pres)/len(cont_pres)
        writer.writerow([my_iter1,my_iter2,x,result1,result2])
    
createResults()
myOdb.close()  