import random

datapath = "/home/cwq/TSPHS/test/cwq-test-data/validation_tsp2d/tsp_min-n=15_max-n=20_num-graph=100_type=clustered/"
datadir = datapath + "tsp2d_n=19_seed=192713.tsp" 

with open(datadir, 'r') as f_tsp:
    for l in f_tsp:     # each line 
        if 'DIMENSION' in l:
            n_nodes = int(l.split(' ')[-1].strip())
            break

random_charger = random.randint(1, n_nodes)  # This will generate a random integer between 1 and 10 (inclusive).                       
with open(datadir, 'a') as f_tsp:
    f_tsp.write("\nNODE_CHARGER_SECTION")
    for i in range(n_nodes):
        if i == random_charger:
            f_tsp.write("\n%d %d" % (i+1, 1))
        else:
            f_tsp.write("\n%d %d" % (i+1, 0)) 
    