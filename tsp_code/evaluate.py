import numpy as np
import networkx as nx
# import cPickle as cp
import random
import ctypes
import os
import sys
import time
from tqdm import tqdm
import scipy.io as scio  

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
    api = Tsp2dLib(sys.argv)        # initilize （new) the test_env
    
    opt = {}
    # for i in range(1, len(sys.argv), 2):
    #     opt[sys.argv[i][1:]] = sys.argv[i + 1]
    
    
    g_type='clustered'    
    result_root='/home/myhan/tsphs/tsp_code/results/dqn-%s'% g_type

    test_min_n=15
    test_max_n=20

    # max belief propagation iteration
    max_bp_iter=4

    # embedding size
    embed_dim=64

    # gpu card id
    dev_id=0

    # max batch size for training/testing
    batch_size=128

    net_type='QNet'
    decay=0.1

    # set reg_hidden=0 to make a linear regression
    reg_hidden=32

    # learning rate
    learning_rate=0.0001

    # init weights with rand normal(0, w_scale)
    w_scale=0.01

    # nstep
    n_step=1

    knn=10

    min_n=15
    max_n=20

    num_env=1
    mem_size=50000

    max_iter=200000

    # folder to save the trained model
    # save_dir=$result_root/ntype-$net_type-embed-$embed_dim-nbp-$max_bp_iter-rh-$reg_hidden
    save_dir=result_root+'/ntype-%s-embed-%d-nbp-%d-rh-%d' %(net_type, embed_dim, max_bp_iter, reg_hidden)

    opt.update({'net_type': net_type, 
                'dev_id': dev_id, 
                'n_step': n_step, 
                'data_root': '/data/myh/tsp2d_charger', 
                'decay': decay, 
                'knn': knn, 
                'test_min_n': str(test_min_n) ,
                'test_max_n': str(test_max_n), 
                'min_n': str(min_n), 
                'max_n': str(max_n), 
                'num_env': num_env, 
                'max_iter': max_iter, 
                'mem_size': mem_size, 
                'g_type': g_type, 
                'learning_rate': learning_rate, 
                'max_bp_iter': max_bp_iter, 
                'save_dir': save_dir, 
                'embed_dim': embed_dim, 
                'batch_size': batch_size, 
                'reg_hidden': reg_hidden, 
                'momentum': 0.9, 
                'l2': 0.00, 
                'w_scale': w_scale,
                'g_type': 'clustered',})
    

    model_file = find_model_file(opt)
    assert model_file is not None
    print('loading', model_file)
    sys.stdout.flush()
    model_file = model_file.encode('utf-8')
    api.LoadModel(model_file)       # qnet model

    test_name = '-'.join([opt['g_type'], opt['test_min_n'], opt['test_max_n']]) 
    result_file = '%s/Atest-%s-gnn-%s-%s.csv' % (opt['save_dir'], test_name, opt['min_n'], opt['max_n'])

    n_test = 1000
    frac = 0.0
    with open(result_file, 'w') as f_out:
        print('testing')
        sys.stdout.flush()
        idx = 0
        for g in tqdm(TestSet()):
            api.InsertGraph(g, is_test=True) 
            
            t1 = time.time()
            val, sol, sol_state_already_list, soc_list = api.GetSol(idx, nx.number_of_nodes(g))
            t2 = time.time()
            f_out.write('%.8f,' % val)
            f_out.write('%d' % sol[0])
            chargers = nx.get_node_attributes(g, 'isCharger')
            # for i in range(min(len(soc_list), max_n + 10)):
            #     print('soc_list[{}]:'.format(i), soc_list[i])
            # print('soc_list:', soc_list)
            
            # soc_seq = nx.get_node_attributes(g, 'soc_seq')  
            for i in range(sol[0]):
                node_id = sol[i + 1]
                node_id_new = sol_state_already_list[i + 1]
                soc_id = soc_list[i + 1]
                # soc_seq_i = soc_seq.get(node_id, [0])
                # soc = soc_seq_i[-1] if soc_seq_i else 0  # 获取 soc_seq 的最后一个值，如果 soc_seq 为空，则 soc 为 0                
                is_charge = chargers[node_id_new]
                # f_out.write(' %d' % node_id)
                f_out.write(' %d(SOC=%.6f)' % (node_id_new, soc_id))
                if is_charge:
                    f_out.write('(c)')
            f_out.write(',%.6f\n' % (t2 - t1))
            frac += val            

            idx += 1
    print('frac: ', frac)
    print('average tour length: ', frac / n_test)
