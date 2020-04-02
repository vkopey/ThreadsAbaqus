# -*- coding: cp1251 -*-
'''модель замкового різьбового зєднання (ГОСТ 5286-75)'''
if _my_thread_model!=2: from tools import *

zn80={'D':(80,-0.5,0.5),#зовнішній діаметр труби ніпеля
    'D1':(76.5,-0.5,0.5),#зовнішній діаметр упорного торця
    'd3':(25.0,-0.6,0.6),#внутрішній діаметр ніпеля
    'd4':(36.0,-0.6,0.6),#внутрішній діаметр муфти
    'L2':(240.0,0.0,0.0),#довжина муфти*
    'dsr':(60.080,0.0,0.0),#середній діаметр різьби в основній площині
    'd5':(66.674,0.0,0.0),#діаметр більшої основи конуса ніпеля*
    'd6':(47.674,0.0,0.0),#діаметр меншої основи конуса ніпеля*
    'l3':(76.0,-2.0,0),#довжина конуса ніпеля
    'd7':(68.3,-0.6,0.6),#діаметр конічної виточки в площині торця муфти
    'd8':(61.422,0.0,0.0),#внутрішній діаметр різьби в площині торця муфти*
    'l4':(82.0,0.0,0.0),#відстань від торця до кінця різьби з повним профілем муфти (не менше)
    'P':(5.080,0.0,0.0),#крок різьби паралельно осі різьби
    'fi':(atan(0.25/2)*180/pi,0.0,0.0),#кут нахилу
    'H':(4.376,0.0,0.0),#висота гострокутного профілю
    'h1':(2.993,0.0,0.0),#висота профілю різьби
    'h':(2.626,0.0,0.0),#робоча висота профілю
    'l':(0.875,0.0,0.0),#висота зрізу вершин
    'f':(0.508,0.0,0.0),#відтин впадини
    'a':(1.016,0.0,0.0),#площадка*
    'r':(0.508,0.0,0.0),#радіус заокруглень впадин*
    'r_':(0.38,0.0,0.0)}#радіус спряжень (не більше)
zn95={'D':(80, -0.5, 0.5),
    'D1':(76.5,-0.5,0.5),
    'd3':(25.0,-0.6,0.6),
    'd4':(36.0,-0.6,0.6),
    'L2':(240.0,0.0,0.0),
    'dsr':(60.080,0.0,0.0),
    'd5':(66.674,0.0,0.0),
    'd6':(47.674,0.0,0.0),
    'l3':(76.0,-2.0,0),
    'd7':(68.3,-0.6,0.6),
    'd8':(61.422,0.0,0.0),
    'l4':(82.0,0.0,0.0),
    'P':(5.080,0.0,0.0),
    'fi':(atan(0.25/2)*180/pi,0.0,0.0),
    'H':(4.376,0.0,0.0),
    'h1':(2.993,0.0,0.0),
    'h':(2.626,0.0,0.0),
    'l':(0.875,0.0,0.0),
    'f':(0.508,0.0,0.0),
    'a':(1.016,0.0,0.0),
    'r':(0.508,0.0,0.0),
    'r_':(0.38,0.0,0.0)}

zamok={80:zn80,95:zn95}#словник типорозмірів
diameter=80#типорозмір
d={}#словник усіх розмірів моделі
for x in zamok[diameter].iterkeys():
    d[x]=Dim(zamok[diameter][x])#копіюємо ключі, а значення перетворюємо в розміри Dim

d['D'].v=d['D'].min()/2
d['D1'].v=d['D1'].min()/2
d['d3'].v=d['d3'].max()/2
d['d4'].v=d['d4'].max()/2
d['L2'].v=d['L2'].n/2
d['dsr'].v=d['dsr'].n/2
d['d5'].v=d['d5'].n/2
d['d6'].v=d['d6'].n/2
d['l3'].v=d['l3'].min()
d['d7'].v=d['d7'].max()/2
d['d8'].v=d['d8'].max()/2
d['l4'].v=d['l4'].n
d['P'].v=d['P'].n
d['fi'].v=d['fi'].n
d['H'].v=d['H'].n
d['h1'].v=d['h1'].n
d['h'].v=d['h'].n
d['l'].v=d['l'].n
d['f'].v=d['f'].n
d['a'].v=d['a'].n
d['r'].v=d['r'].n
d['r_'].v=d['r_'].n
#================точки характерних кромок моделі========================
en1=((d['D'].v+d['d3'].v)/2,d['l3'].v+20.0,0.0)#верхній торець ніпеля
en2=(d['d3'].v,d['l3'].v/2,0.0)#внутрішній циліндр ніпеля
en3=(d['D'].v,d['l3'].v+10.0,0.0)#зовнішній циліндр ніпеля
em1=((d['D'].v+d['d4'].v)/2,d['l3'].v-d['L2'].v,0.0)#нижній торець муфти
em2=(d['D'].v,0.0,0.0)#зовнішній циліндр муфти
em3=(d['d4'].v,d['l3'].v-d['L2'].v+5.0,0.0)#внутрішній циліндр муфти
em4=((d['D'].v+d['d7'].v)/2,d['l3'].v-8.0,0.0)#близько центру Partition face-1 (для Bolt Load)
mat1=matlib['40'].power(8)#матеріал 1
mat2=Material(E=210000.0e+6,mu=0.28,st=my_iter2*1e+6,sv=750.0e+6,delta=18.0,psi=60.0).power(8)#матеріал 2
bolt_load=-my_iter1 #-0.1
load1=-1
load2=-155.1e+6 #-1.0e+6/(pi*(d['D'].v/1000)**2-pi*(d['d3'].v/1000)**2)#або в нютонах

def createProfile():
    "Створює профіль різьби ніпеля і муфти"
    #створення профілю різьби ніпеля
    createCut(Part='Part-1',Sketch='Sketch-3',Begin=0,P=d['P'].v,Fi=d['fi'].v,Len=d['l3'].v-15.875+d['P'].v,X=d['dsr'].v,Y=d['l3'].v-15.875,dx=-1,dy=-1)
    #збіг різьби ніпеля
    createCut(Part='Part-1',Sketch='Sketch-3',Begin=1,P=d['P'].v,Fi=d['fi'].v,Len=6.35,X=d['dsr'].v,Y=d['l3'].v-15.875,dx=1,dy=1)
    #створення профілю різьби муфти
    createCut(Part='Part-2',Sketch='Sketch-4',Begin=0,P=d['P'].v,Fi=d['fi'].v,Len=d['l4'].v-16,X=d['dsr'].v,Y=d['l3'].v-15.875,dx=-1,dy=-1)

#параметри заготовки ніпеля
par={'l3':d['l3'].v,'d6':d['d6'].v,'fi':d['fi'].v,'D':d['D'].v,'D1':d['D1'].v,
     'd3':d['d3'].v}
set_values(sketch='Sketch-1',p=par)
#параметри заготовки муфти
par={'l3':d['l3'].v,'l4':d['l4'].v+2,'fi':d['fi'].v,'D':d['D'].v,'d4':d['d4'].v,
     'L2':d['L2'].v,'D1':d['D1'].v,'d7':d['d7'].v,'d8':d['d8'].v}
set_values(sketch='Sketch-2',p=par)
#параметри профілю різьби ніпеля
par={'fi':d['fi'].v,'H_21':d['H'].v/2,'H_22':d['H'].v/2,'r':d['r'].v}
set_values(sketch='Sketch-3',p=par)
#параметри профілю різьби муфти
par={'fi':d['fi'].v,'H_21':d['H'].v/2,'H_22':d['H'].v/2,'r':d['r'].v}
set_values(sketch='Sketch-4',p=par)

createPart(n='Part-1',s='Sketch-1')
createPart(n='Part-2',s='Sketch-2')
createProfile()
createPartition(part='Part-2',offset=d['l3'].v-8.0)
createMaterial('Material-1',et=mat1['el'],pt=mat1['pl'])
createMaterial('Material-2',et=mat2['el'],pt=mat2['pl'])
createSectionAssign(n='Section-1',m='Material-1',p='Part-1')
createSectionAssign(n='Section-2',m='Material-2',p='Part-2')
createAssemblyInstance(n='Part-1-1',p='Part-1')
createAssemblyInstance(n='Part-2-1',p='Part-2')
createStep(n='Step-1',pr='Initial')
createStep(n='Step-2',pr='Step-1')
createContactSet(n='Slave',i='Part-1-1',ep=((en1, ), (en2, ), (en3, ),))#створюємо набір кромок контакту для ніпеля
createContactSet(n='Master',i='Part-2-1',ep=((em1, ), (em2, ),(em3, ),(em4, ),))#створюємо набір кромок контакту для муфти
createContactProperty()
createContact()
createBCSet(n='Pressure',i='Part-1-1',ep=(en1, ))#тиск
createBCSet(n='Encastre',i='Part-2-1',ep=(em1, ))#закріплення
createBC_Pressure([('Step-1',load1),('Step-2',load2)])
createBC_Encastre()
createBC_BoltLoad('Part-2-1',em4,bolt_load)
createMesh()
createEdgesSet(n='Cont',i='Part-2-1',p=((((36.725, 74.0, 0)), ),) )
createEdgesSet(n='First',i='Part-1-1',p=(((27.725, 53.045, 0), ),) )
createJobSubmit()

myOdb = openOdb(path=model.name + '.odb')
def createResults():
    session.viewports['Viewport: 1'].setValues(displayedObject=myOdb)
    SF_field()       
    cont_pres=readODB_set(set='Cont',step='Step-2',var=(('CPRESS', ELEMENT_NODAL), ),pos=NODAL)
    result1=sum(cont_pres)/len(cont_pres)
    result2=min(readODB_set2(set='First',step='',var=('D',''),pos=INTEGRATION_POINT))
    result3=max(readODB_set(set='First',step='Step-2',var=(('S', INTEGRATION_POINT, ((INVARIANT, 'Mises'), )), ),pos=INTEGRATION_POINT))
    writer.writerow([my_iter1,my_iter2,result1,result2,result3])
    
createResults()
myOdb.close()  