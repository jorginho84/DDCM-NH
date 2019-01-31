


def sub_emax_gen():

		return [emax_t1_ins[0], emax_t1_ins[1]]	
		
		def emax_gen(j):

			emax_dic = {}
			emax_values = {}

			
			for t in range(j,0,-1):
				
				if t==j:#last period
					emax_bigt_ins=self.emax_bigt(j)
					
					
					emax_dic={'emax'+str(t): emax_bigt_ins[0]}
					emax_values={'emax'+str(t): emax_bigt_ins[1]}
				elif t==j-1: #at T-1
					emax_t1_ins=self.emax_t(t,j,emax_bigt_ins[0])
					
					
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]
					
				else:
					emax_t1_ins=self.emax_t(t,j,emax_t1_ins[0])
					
					
					emax_dic['emax'+str(t)]=emax_t1_ins[0]
					emax_values['emax'+str(t)]=emax_t1_ins[1]

			
			list_subemax = pool.map(sub_emax_gen,range(j,0,-1))

			for t in range(j,0,-1):
				emax_dic['emax'+str(t)] = list_subemax[0]
				emax_values['emax'+str(t)]=list_subemax[1]