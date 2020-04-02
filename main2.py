# -*- coding: cp1251 -*-
'''Розрахунок замкового різьбового зєднання'''
_my_thread_model=2
import csv
csv_file=open("results.csv", "wb")
writer = csv.writer(csv_file,delimiter = ';')
writer.writerow(['boltload','sv','cont','Dfirst','Sfirst'])
#my_iter2=0
#my_iter1=0.1
#execfile('tools.py')
#execfile('gost5286_75.py')
for my_iter2 in [100*x for x in range(3,5+1,1)]:#границя текучості матеріалу муфти, МПа
    for my_iter1 in [x/100.0 for x in range(0,30+5,5)]:#величина згвинчування, мм
        execfile('tools.py')
        execfile('gost5286_75.py')
        print 'my_iters=',my_iter1,my_iter2
        Mdb()
        session.viewports['Viewport: 1'].setValues(displayedObject=None)  
csv_file.close()
