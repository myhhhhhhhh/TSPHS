import random
from tqdm import tqdm
 
data_root = '/data/myh/tsp2d_charger'
prefixes = ['validation_tsp2d', 'train_tsp2d', 'test_tsp2d']
prefix_n_graphs = {'validation_tsp2d': 100,
                   'train_tsp2d': 10000,
                   'test_tsp2d': 1000}
min_n_max_n = {'validation_tsp2d': [(15, 20), (40, 50), (50, 100), (100, 200), (200, 300), (300, 400), (400, 500)],
                'train_tsp2d': [(15, 20), (40, 50), (50, 100), (100, 200), (200, 300), (300, 400), (400, 500), (500, 600)],
                'test_tsp2d': [(15, 20), (40, 50), (50, 100), (100, 200), (200, 300), (300, 400), (400, 500), (500, 600), (1000, 1200)]}
g_types = ['clustered', 'random']

prefix = prefixes[2]
n_graphs = prefix_n_graphs[prefix]

for min_max in range(len(min_n_max_n[prefix])):
    min_n, max_n = min_n_max_n[prefix][min_max]
    for g_type in g_types:
        folder = '%s/%s/tsp_min-n=%s_max-n=%s_num-graph=%d_type=%s' % (data_root, prefix, 
                                                               min_n, max_n, n_graphs, g_type)
        with open('%s/paths.txt' % folder, 'r') as f:
            for line in tqdm(f):
                fname = '%s/%s' % (folder, line.split('/')[-1].strip()) 
                n_nodes = -1
                with open(fname, 'r') as fr_tsp:
                        for l in fr_tsp:     # each line 
                            if 'DIMENSION' in l:
                                n_nodes = int(l.split(' ')[-1].strip())
                                break
                random_charger = random.randint(0, n_nodes-1)
                
                with open(fname, 'a') as f_tsp:
                    f_tsp.write("\nNODE_CHARGER_SECTION")
                    for i in range(n_nodes):
                        if i == random_charger:
                            f_tsp.write("\n%d %d" % (i+1, 1))
                        else:
                            f_tsp.write("\n%d %d" % (i+1, 0))                 
                # print("success written!")                
                
                isCharger_all = []
                in_charger = False
                errors = {}
                with open(fname, 'r') as f_tsp:
                    for l in f_tsp:     # each line                         
                        if 'NODE_CHARGER_SECTION' in l:
                            in_charger = True
                            continue
                        if in_charger:
                            idx, isCharger = [int(w.strip()) for w in l.split(' ')]
                            isCharger_all.append(isCharger)
                if sum(isCharger_all) != 1:
                    print("error in %s" % fname)
                    print(sum(isCharger_all)) 
                    errors.update({fname: sum(isCharger_all)})
                # else:
                #     print("success in %s" % fname)
                #     print(sum(isCharger_all))
                    
