"""
execfile('skills_step.py')

This file computes stepdown multiple testing on a set of test scores.
The null hypothesis: no differences between control and treatment groups

pip2.7 install --user --upgrade pylatex

"""
from __future__ import division #omit for python 3.x
import numpy as np
import pandas as pd
import pickle
import itertools
import sys, os
from scipy import stats
#from scipy.optimize import minimize
from scipy.optimize import fmin_bfgs
from joblib import Parallel, delayed
from scipy import interpolate
import matplotlib
matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
import subprocess



####Skills estimates###
dofile = "/mnt/Research/nealresearch/new-hope-secure/newhopemount/codes/skills/skills.do"
cmd = ["stata-mp", "do", dofile]
subprocess.call(cmd)

#pvalues are saved here
pval_dic = {}

#ordering are saved here
order_dic = {}

#obtaining adjusted p-values
for model in range(2): #in every year we have 2 models

	for year in [2,5]:

		if year==2:
			nblocks=2
		elif year==5:
			nblocks=5

		for block in range(nblocks):

			y2_obs_block1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/y' + str(year) + '_obs_block'+str(block+1)+'_model'+str(model+1)+'.csv').values
			y2_res_block1=pd.read_csv('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/y' + str(year) +'_res_block'+str(block+1)+'_model'+str(model+1)+'.csv').values


			#number of hypothesis/replications
			nh = y2_res_block1.shape[1]
			nr = y2_res_block1.shape[0]

			#Ordering hypotheses
			y2_obs_block1_or = -np.sort(-y2_obs_block1)
			inds=(-y2_obs_block1[0,:]).argsort()
			y2_res_block1_or = y2_res_block1[:,inds]
			order_dic['Y' + str(year) +'_block' + str(block + 1)] = inds

			#The Max matrix: (S hypotheses x resamples)
			max_matrix = np.zeros((nr,nh))
			for m in range(nr):
				for j in range(nh):
					max_matrix[m,j] = np.max(y2_res_block1_or[m,j:])


			#The adjusted p-values
			pvalues = np.zeros((nh,))

			# for the first hypothesis
			boo_max = max_matrix[:,0]>=y2_obs_block1_or[0,0] 
			pvalues[0] = (np.sum(max_matrix[:,0]>=y2_obs_block1_or[0,0] ) + 1)/(nr+1)

			#for the rest
			for j in range(1,nh):
				p_initial = (np.sum(max_matrix[:,j]>=y2_obs_block1_or[0,j] ) + 1)/(nr+1)
				pvalues[j] = np.max(np.array([p_initial,pvalues[j-1]]))
			 
			 #save in pvalue dic

			pval_dic['Y' + str(year) + '_Block' + str(block+1)+'_model'+str(model+1)] = pvalues


##Writing the table


###Year-2 Table###
#The list of tests
tests_list_block1 = ['Overall', 'Reading', 'Math', 'Reading grade expectations','Math grade expectations', 'Motivation', 'Parental encouragement','Intellectual functioning', 'Classroom behavior', 'Communication skills']
tests_list_block2 = ['Behavior skills', 'Independent skills', 'Transitional skills']


with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/Y2_pvalues.tex','w') as f:
	f.write(r'\begin{tabular}{lcccc}'+'\n')
	f.write(r'\hline')
	f.write(r'  \textbf{Measures}    &       & \textbf{No controls} &       & \textbf{W/ controls} \bigstrut[b] \\' + '\n')
	f.write(r'\cline{1-1}\cline{3-3}\cline{5-5}'+'\n')
	f.write(r'      &       &       &       &  \\' + '\n')
		
	#block 1
	f.write(r'\multicolumn{5}{l}{\textbf{Panel A. SSRS Academic Subscale}} \bigstrut[t]\\' + '\n')
	for j in range(len(tests_list_block1)):
		f.write(tests_list_block1[order_dic['Y2_block1'][j]] + r'& &' 
			+'{:04.3f}'.format(pval_dic['Y2_Block1_model1'][j])+ r'&  & ' 
			+'{:04.3f}'.format(pval_dic['Y2_Block1_model2'][j])+ r'\\'+'\n')
		
	#block 2
	f.write(r'\multicolumn{5}{l}{\textbf{Panel B. Classroom Behavior Scale}} \\' + '\n')
	for j in range(len(tests_list_block2)):
		f.write(tests_list_block2[order_dic['Y2_block2'][j]] + r'& &' 
			+'{:04.3f}'.format(pval_dic['Y2_Block2_model1'][j])+ r'&  & ' 
			+'{:04.3f}'.format(pval_dic['Y2_Block2_model2'][j])+ r'\\'+'\n')
		
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}')
	f.close()



###Year-5 Table###
tests_list_block1 = ['Letter-Word', 'Comprehension', 'Calculation', 'Applied problems']

tests_list_block2 = ['Overall', 'Reading', 'Math', 'Reading grade expectations', 
'Math grade expectations', 'Motivation', 'Parental encouragement',
'Intellectual functioning', 'Classroom behavior', 'Communication skills']

tests_list_block3 = ['Reading', 'Oral language', 'Written language', 'Math', 
'Social studies', 'Science']

tests_list_block4 = ['Behavior skills', 'Independent skills', 'Transitional skills']

tests_list_block5 = ['Reading', 'Math', 'Written work', 'Overall']

tests_list  = [tests_list_block1, tests_list_block2, tests_list_block3,
 tests_list_block4, tests_list_block5]

block_list = ['Panel A. Woodcock-Johnson', 'Panel B. SSRS Academic Subscale',
'Panel C. Teachers Mock\' Reports Cards', 'Panel D. Classroom Behavior Scale',
'Panel D. Parents\' Reports' ]

with open('/mnt/Research/nealresearch/new-hope-secure/newhopemount/results/Skills/Y5_pvalues.tex','w') as f:
	f.write(r'\begin{tabular}{lcccc}'+'\n')
	f.write(r'\hline')
	f.write(r' \textbf{Measures}     &       & \textbf{No controls} &       & \textbf{W/ controls} \bigstrut[b] \\' + '\n')
	f.write(r'\cline{1-1}\cline{3-3}\cline{5-5}'+'\n')
	f.write(r'      &       &       &       &  \\' + '\n')
	
	for b in range(5):#blocks
	#block 1
		f.write(r'\multicolumn{5}{l}{\textbf{' + block_list[b] + r'}} \bigstrut[t]\\' + '\n')
		for j in range(len(tests_list[b])):
			f.write(tests_list[b][order_dic['Y5_block' + str(b+1)][j]] + r'& &' 
				+'{:04.3f}'.format(pval_dic['Y5_Block'+ str(b+1) +'_model1'][j])+ r'&  & ' 
				+'{:04.3f}'.format(pval_dic['Y5_Block' + str(b+1) + '_model2'][j])+ r'\\'+'\n')
			
	f.write(r'\hline'+'\n')
	f.write(r'\end{tabular}')
	f.close()


