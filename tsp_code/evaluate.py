import numpy as np
import networkx as nx
# import cPickle as cp
import random
import ctypes
import os
import sys
import time
from tqdm import tqdm

sys.path.append( '%s/tsp2d_lib' % os.path.dirname(os.path.realpath(__file__)) )
from tsp2d_lib.tsp2d_lib import Tsp2dLib
    
def find_model_file(opt):
    max_n = int(opt['max_n'])
    min_n = int(opt['min_n'])
    log_file = '%s/log-%d-%d.txt' % (opt['save_dir'], min_n, max_n)

    best_r = 10000000
    best_it = -1
    with open(log_file, 'r') as f:
        for line in f:
            if 'average' in line:
                line = line.split(' ')
                it = int(line[1].strip())
                r = float(line[-1].strip())
                if r < best_r:
                    best_r = r
                    best_it = it
    assert best_it >= 0
    print('using iter=', best_it, 'with r=', best_r)
    return '%s/nrange_%d_%d_iter_%d.model' % (opt['save_dir'], min_n, max_n, best_it)

def TestSet():
    folder = '%s/test_tsp2d/tsp_min-n=%s_max-n=%s_num-graph=1000_type=%s' % (opt['data_root'], opt['test_min_n'], opt['test_max_n'], opt['g_type'])

    with open('%s/paths.txt' % folder, 'r') as f:
        for line in f:
            fname = '%s/%s' % (folder, line.split('/')[-1].strip())
            coors = {}
            chargers = {}
            in_sec = False
            in_charger = False
            n_nodes = -1
            with open(fname, 'r') as f_tsp:
                for l in f_tsp:
                    if 'DIMENSION' in l:
                        n_nodes = int(l.split(' ')[-1].strip())
                    elif 'NODE_COORD_SECTION' in l:
                        in_sec = True
                        in_charger = False
                        continue
                    elif 'NODE_CHARGER_SECTION' in l:
                        in_charger = True
                        in_sec = False
                        continue
                    elif l == '\n':
                        in_sec = False
                        in_charger = False
                    if in_sec:
                        idx, x, y = [int(w.strip()) for w in l.split(' ')]
                        coors[idx - 1] = [float(x) / 1000000.0, float(y) / 1000000.0]
                        assert len(coors) == idx                    
                    elif in_charger:
                        idx, isCharger = [int(w.strip()) for w in l.split(' ')]
                        chargers[idx - 1] = isCharger
                        assert len(chargers) == idx 
            assert len(coors) == n_nodes
            g = nx.Graph()
            g.add_nodes_from(range(n_nodes))
            nx.set_node_attributes(g, coors, 'pos')
            nx.set_node_attributes(g, chargers, 'isCharger')
            
            yield g            

if __name__ == '__main__':
    api = Tsp2dLib(sys.argv)
    
    opt = {}
    for i in range(1, len(sys.argv), 2):
        opt[sys.argv[i][1:]] = sys.argv[i + 1]

    model_file = find_model_file(opt)
    assert model_file is not None
    print('loading', model_file)
    sys.stdout.flush()
    model_file = model_file.encode('utf-8')
    api.LoadModel(model_file)

    test_name = '-'.join([opt['g_type'], opt['test_min_n'], opt['test_max_n']])
    result_file = '%s/test-%s-gnn-%s-%s.csv' % (opt['save_dir'], test_name, opt['min_n'], opt['max_n'])

    n_test = 1000
    frac = 0.0
    with open(result_file, 'w') as f_out:
        print('testing')
        sys.stdout.flush()
        idx = 0
        for g in tqdm(TestSet()):
            api.InsertGraph(g, is_test=True)
            t1 = time.time()
            val, sol, soc_list = api.GetSol(idx, nx.number_of_nodes(g))
            t2 = time.time()
            f_out.write('%.8f,' % val)
            f_out.write('%d' % sol[0])
            chargers = nx.get_node_attributes(g, 'isCharger')
            # soc_seq = nx.get_node_attributes(g, 'soc_seq')  
            for i in range(sol[0]):
                node_id = sol[i + 1]
                soc_id = soc_list[i+1]
                # soc_seq_i = soc_seq.get(node_id, [0])
                # soc = soc_seq_i[-1] if soc_seq_i else 0  # 获取 soc_seq 的最后一个值，如果 soc_seq 为空，则 soc 为 0                
                is_charge = chargers[node_id]
                # f_out.write(' %d' % node_id)
                f_out.write(' %d(SOC=%.2f)' % (node_id, soc_id))
                if is_charge:
                    f_out.write('(c)')
            f_out.write(',%.6f\n' % (t2 - t1))
            frac += val
            

            idx += 1

    print('average tour length: ', frac / n_test)
