import time
from multiprocessing import Pool
import random
from  get_source import get_contract_code

# LofL = [([i for i in xrange(0, random.randint(1,100))]) for j in xrange(0,100000)]

# L = ['0x37a9679c41e99db270bda88de8ff50c0cd23f326', '0x209c4784ab1e8183cf58ca33cb740efbf3fc18ef']
L2 = ['0x37a9679c41e99db270bda88de8ff50c0cd23f326', '0x209c4784ab1e8183cf58ca33cb740efbf3fc18ef' , '0xbfc39b6f805a9e40e77291aff27aee3c96915bdd', '0xaa1a6e3e6ef20068f7f8d8c835d2d22fd5116444', '0xbb9bc244d798123fde783fcc1c72d3bb8c189413', '0xfa52274dd61e1643d2205169732f29114bc240b3', '0xe94b04a0fed112f3664e45adb2b8915693dd5ff3', '0x1158c3c9a70e85d8358972810ed984c8e6ffcf0f', '0x7de5aba7de728950c92c57d08e20d4077161f12f', '0xad62f56a03334b647e55dbdb5b8642c24605a801', '0xedbaf3c5100302dcdda53269322f3730b1f0416d', '0x48c80f1f4d53d5951e5d5438b54cba84f29f32a5', '0x9af09991ad63814e53ffc1bccf213ee74027608b', '0x8b3b3b624c3c0397d3da8fd861512393d51dcbac', '0x3589d05a1ec4af9f65b0e5554e645707775ee43c', '0xcd111aa492a9c77a367c36e6d6af8e6f212e0c8e', '0xa43ebd8939d8328f5858119a3fb65f65c864c6dd', '0x7c20218efc2e07c8fe2532ff860d4a5d8287cb31', '0xd588b586d61c826a0e87919b3d1a239206d58bf2', '0x9bcb0733c56b1d8f0c7c4310949e00485cae4e9d', '0x1c39ba39e4735cb65978d4db400ddd70a72dc750', '0xfdc77b9cb732eb8c896b152e28294521f5f62e67', '0x41f274c0023f83391de4e0733c609df5a124c3d4', '0x18a672e11d637fffadccc99b152f4895da069601', '0x57d90b64a1a57749b0f932f1a3395792e12e7055']

def Map(L):
	return [get_contract_code(L)]
 
  # results = []
  # for w in L:
  #   results.append ((get_contract_code(w), 1))
 
  # return results

pool = Pool(processes=8)

print "Length of list - %d" % len(L2)

# print "Starting serial..."
# start_time = time.time()
# e = [Map(l) for l in L2]
# print("Serial - --- %s seconds ---" % (time.time() - start_time))

print "Starting multiprocessing with 8 cores..."
start_time = time.time()
d = pool.map(Map, L2)
print("Parallel - --- %s seconds ---" % (time.time() - start_time))

# print "Starting multiprocessing with 20 cores..."
# pool2 = Pool(processes=20)
# start_time = time.time()
# f = pool2.map(Map, L2)
# print("Parallel - --- %s seconds ---" % (time.time() - start_time))