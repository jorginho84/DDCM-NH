"""
exec(open("/home/jrodriguez/NH_HC/codes/model_v2/ses/draft.py").read())


This file computes standard errors of structural parameters

"""


for k in [4]:

		V1_1 = np.dot(np.transpose(dbdt[k]),w_matrix)
		
		V1 = np.linalg.inv(np.dot(V1_1,dbdt[k]))

		V2 = np.dot(np.dot(V1_1,var_cov),np.transpose(V1_1))

		vc = np.dot(np.dot(V1,V2),V1)
		
		se_list = []
		se_list.append(np.sqrt(np.diagonal(vc*(1+1/M))))

		df = pd.DataFrame(se_list)

		df.to_csv('/home/jrodriguez/NH_HC/codes/model_v2/ses/se_'+str(k)+'.csv', index=False)




