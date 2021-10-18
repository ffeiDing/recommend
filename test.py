import scipy.sparse as ss

W = ss.lil_matrix((5, 5))
W[0,1] += 1
print(W)
print(W.todense())