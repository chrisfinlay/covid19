import numpy as np

def standard(Ni, r, days):

    return Ni*r**np.arange(days)

def linear_rate(Ni, r, w, x, days):

    return Ni*(r+np.sum(w*x))**np.arange(days)
