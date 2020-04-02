# -*- coding: cp1251 -*-
'''Розрахунок різьбового зєднання НКТ'''
_my_thread_model=3
import csv
csv_file=open("results.csv", "wb")
writer = csv.writer(csv_file,delimiter = ';')
writer.writerow(['boltload','press','n','cont_work','cont_nwork'])
#my_iter2=155.1
#my_iter1=0
#execfile('tools.py')
#execfile('gost633_80.py')
for my_iter2 in [0.000001,100,200,300]:
    for my_iter1 in [0,1,2]:
        execfile('tools.py')
        execfile('gost633_80.py')
        print 'my_iters=',my_iter1,my_iter2
        Mdb()
        session.viewports['Viewport: 1'].setValues(displayedObject=None)  
csv_file.close()
