
# coding: utf-8

'''
visualizes errors for different as graph. matplotlib
'''
# In[2]:

import matplotlib.pylab as plt
import numpy as np


# In[14]:

#x - alpha
alphas = np.arange(0.81,1,0.01)



#errors for olmaz ilaç
errorMeans = [ 2.13, 2.13, 2.03, 1.65, 1.44,1.34, 1.3, 1.07, 1.07, 1.06, 1.07, 0.9, 0.9, 0.89, 0.63, 0.13, 0.13, 0.13, 0.12 ]
errorStDev = [2.18,  2.18, 2.22, 2.13, 2.09, 2.12, 2.14, 1.86, 1.86, 1.86, 1.87, 1.86, 1.85,1.85,  1.75, 0.17, 0.16, 0.17, 0.15]



# In[15]:

len(alphas)


# In[ ]:


plt.plot(alphas,errorMeans, 'r^', alphas, errorStDev, 'bs' )
plt.show()


# In[ ]:



