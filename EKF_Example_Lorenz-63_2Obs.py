from KF_Plot import *
from tqdm import tqdm

k = 2000 # number of steps      
m = 3 # dimension of X
j = 2 # dimension of Y

dt = 0.01
def L63(x):
    dxdt = 10. * (x[1] - x[0])
    dydt = x[0] * (28. - x[2]) - x[1]
    dzdt = x[0] * x[1] - (8./3.) * x[2]
    return np.array([dxdt,dydt,dzdt])

def RK4(x):    
    k1 = L63(x)
    k2 = L63(x + 0.5*k1*dt)
    k3 = L63(x + 0.5*k2*dt)
    k4 = L63(x + k3*dt)
    return x + dt*(k1+2*k2+2*k3+k4)/6 

def M(x):
    return RK4(x)

def M_j(x): # Jacobian of M
    s=10
    r=28
    b=8/3
    # return np.array([[1-dt*s, dt*s, 0],[dt*r-x[2][0], 0, -dt*x[0][0]],[dt*x[1][0], dt*x[0][0], 1-dt*b]])
    return np.array([[-s, s, 0.], [r-x[2][0], -1, x[0][0]], [x[1][0], x[0][0], -b]])

def H(x): # Observation Operator
    return np.array([x[0],x[1]])
def H_j(x):
    return np.array([[1,0,0],[0,1,0]])

# Q = np.zeros((m,m)) # Model error (assume no model error)
Q = np.diag([0.0001,0.0001,0.0001])
# Q = np.diag([0.0001,0.0001,0.0001])
R = np.diag([0.1, 0.1]) # Observation Error

# true states 
       # starting point
xt0 = np.array([[1],[1],[1.05]])
xt = xt0
Ys = np.array([xt0[0], xt0[2]])

c = 5 # observation Frequency

for i in range(k):
    x = M(xt[:,-1]) 
    xt = np.column_stack((xt,x))

P = np.diag([1,1,1]) # background Covariance 
e = np.random.multivariate_normal([0, 0, 0], P, size=(1)).T # background error
X0 = xt0 + e # background X

ekf = EKF(m, j, X0, P, M, Q, R, H, M_j, H_j)
enkf = StochasticEnKF(m, j, X0, P, M, Q, R, H, H_j, n=10)

for i in tqdm(range(k),desc="Filtering"):
    if i % c == 0:
        ekf.eForecast()
        enkf.enForecast()
        mu = np.random.multivariate_normal([0]*j, R).reshape((j,1)) # observations with error
        y = np.array([[xt[:,i+1][0]], [xt[:,i+1][1]]]) + mu
        ekf.eAnalyze(y)
        enkf.enAnalyze(y)
        Ys = np.column_stack((Ys, y))
    else:
        ekf.eForward()
        enkf.enForward()
        Ys = np.column_stack((Ys, np.array([[np.inf],[np.inf]])))
    ekf.RMSDSave(ekf.X_cStack, xt)
    enkf.RMSDSave(enkf.X_cStack, xt)

# ekf.plot_all(xt,has_obs=[0],Ys=Ys,plotXm=False)
# ekf.plot_one(0, xt, 0, Ys)
# ekf.plot_two(0, 1, xt, ym1=0, Ys=Ys) 
ekf.compare_all(enkf, xt, has_obs=[0], Ys=Ys, plotXm=False, show=False)

ekf.plot_RMSD(filters=[enkf], show=False)

plt.show()

