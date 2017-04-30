
# coding: utf-8

# In[21]:

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab
import math

fig1 = plt.figure() 

mean = 1
variance = 0.05
sigma = math.sqrt(variance)
x = np.linspace(0,2,100)
plt.plot(x,mlab.normpdf(x,mean,sigma))
plt.xlabel('d', fontsize=40)
plt.ylabel('p(d | ph=''r'')', fontsize=40)
plt.show()
fig1.savefig('/Users/joro/Documents/Phd/UPF/papers/DurationHSMM_polyphonic_poster/poster_5_r.svg')


# In[ ]:



