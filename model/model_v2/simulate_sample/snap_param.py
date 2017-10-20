"""
execfile('snap_param.py')
This file generates a list of snap parameters
"""

from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import itertools
import sys, os
import pickle
from scipy import stats

#save dictionary here
snap_list = []

#max B: a 9x10 matrix (family size x calendar years)
maxb = pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases/maxb_long.csv',header=None).values

#Standard deductions: a 4x10 matrix (family size x calendar years)
std = pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases/std_long.csv',header=None).values

#Net income test: a 9x10 matrix (family size x calendar years)
ni = pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases/netincome_long.csv',header=None).values

#gross income test: a 9x10 matrix (family size x calendar years)
gi = pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/Data/databases/grossincome_long.csv',header=None).values


snap_dic = {'max_benefit': maxb*12, 'std_deduction': std*12, 'net_income_test': ni*12,
'gross_income_test': gi}

snap_list.append(snap_dic)

#saving list
pickle.dump(snap_list,open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/model_v2/simulate_sample/snap_list.p','wb'))