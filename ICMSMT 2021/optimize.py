# -*- coding: utf-8 -*-
import pickle,subprocess
import numpy as np
from scipy.optimize import minimize, differential_evolution, dual_annealing

def simulate(x):
    with open("x.pkl", "wb") as f:
        pickle.dump(x,f)

    print("Abaqus CAE started. Please wait")
    # виконує скрипт в Abaqus та чекає завершення
    subprocess.Popen(r'c:\SIMULIA\Abaqus\6.14-2\code\bin\abq6142.exe cae noGUI=main2.py').communicate()
    #os.system(r'start /WAIT abaqus cae noGUI=main2.py')
    print("Abaqus CAE finished")
    
    with open('y.pkl', 'rb') as f:
        y=pickle.load(f)
    return y

i=0
Min=0
xopt=None
def f(x_):
    global i,Min,xopt
    
    # для "BFGS"
    print(x_)
    n=np.arange(1.,14)
    x=x_[0]*np.log(n) + x_[1] #x_[0]+x_[1]*n 
    if np.any(((x0+0.1)<x)|(x<(x0-0.1))): return 0.0
    
    y=simulate(x)
    i=i+1
    print(i)
    print(x)
    print(np.array(y))
    if -min(y)<Min:
        Min=-min(y)
        xopt=x
    print("opt=", xopt, Min)
    print("----------------------")
    return -min(y)

#x0=np.array([0.,0.,-0.02,-0.04,-0.06,-0.08,-0.1,-0.12,-0.14,-0.16,-0.18,-0.2,-0.22])
#x0=0.1202-0.0212*np.arange(1.,14)
#x0=0.1249-0.0234*np.arange(1.,14)+0.0003*np.arange(1.,14)**2
#x0=np.array([0.10144525, 0.08111784, 0.05918799, 0.03322708, 0.01217899, -0.00669204, -0.03142165, -0.04669722, -0.06838361, -0.07148969, -0.09582285, -0.126148, -0.13779098])
x0=-0.097*np.log(np.arange(1.,14)) + 0.1447
f(x0) # тест

bounds=np.zeros((13,2))
bounds[:,0]=x0-0.1
bounds[:,1]=x0+0.1
#res=minimize(f, x0=x0, method="L-BFGS-B", bounds=bounds) # знайти мінімум
res=minimize(f, x0=[-0.097, 0.1447], method="BFGS", options={'eps':0.001,'disp':True,'maxiter':100})
#res = differential_evolution(f, bounds=bounds) 
#res = differential_evolution(f, bounds=bounds, popsize=15, init=[x0.copy(),x0.copy()*1.1,x0.copy()*1.09,x0.copy()*1.08,x0.copy()*1.07,x0.copy()*1.06,x0.copy()*1.05,x0.copy()*1.04,x0.copy()*0.99,x0.copy()*0.98,x0.copy()*0.97,x0.copy()*0.96,x0.copy()*0.95,x0.copy()*0.94,x0.copy()*0.93], polish=False) #funEval=(maxiter + 1) * popsize * len(x)
#res = dual_annealing(f, no_local_search=True, x0=[0.1202,-0.0212,0,0], bounds=[(-1.0, 1.0),(-0.1, 0.1),(-0.01, 0.01),(-0.001, 0.001)], maxfun=100)#
print(res)
