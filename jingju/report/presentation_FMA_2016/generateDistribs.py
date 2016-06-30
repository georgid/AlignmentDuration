# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import matplotlib.pyplot as plt
from scipy.stats import expon
import numpy as np
import matplotlib.mlab as mlab
import math

# normal distr
mu = 0
variance = 2
sigma = math.sqrt(variance)
x = np.linspace(-3, 3, 100)
plt.clf()
plt.plot(x,mlab.normpdf(x, mu, sigma), 'g', lw=5)
# expo distr
x = np.linspace(expon.ppf(0.01),expon.ppf(0.99), 100)
# plt.plot(x, expon.pdf(x),'r-', lw=5, alpha=0.6, label='expon pdf')

plt.axis('off')
# plt.show()
plt.savefig("/media/georgid/Cruzer/tmp/report/presentation_FMA_2016/normal_distr_var2")

# <codecell>


