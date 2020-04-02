# -*- coding: cp1251 -*-
'''Розрахунок муфтового різьбового зєднання насосних штанг'''
_my_thread_model=1
import csv
csv_file=open("results.csv", "wb")
writer = csv.writer(csv_file,delimiter = ';')
writer.writerow(['boltload','groove','cont','D','first','centr'])
my_iter2=0
my_iter1=0.1
execfile('tools.py')
execfile('gost13877_96.py')
#for my_iter2 in [10*x for x in range(0,3+1,1)]:
#    for my_iter1 in [x/100.0 for x in range(0,30+5,5)]:
#        execfile('tools.py')
#        execfile('gost13877_96.py')
#        print 'my_iters=',my_iter1,my_iter2
#        Mdb()
#        session.viewports['Viewport: 1'].setValues(displayedObject=None)  
csv_file.close()
