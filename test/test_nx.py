import sys
import networkx as nx
from tqdm import tqdm
print(sys.path)


def PrepareGraphs(isValid):
    if isValid:
        n_graphs = 100
        prefix = 'validation_tsp2d'
    else:
        n_graphs = 10000
        prefix = 'train_tsp2d'
    folder = '%s/%s/tsp_min-n=%s_max-n=%s_num-graph=%d_type=%s' % (opt['data_root'], prefix, opt['min_n'], opt['max_n'], n_graphs, opt['g_type'])

    with open('%s/paths.txt' % folder, 'r') as f:
        for line in tqdm(f):
            fname = '%s/%s' % (folder, line.split('/')[-1].strip())
            coors = {}
            in_sec = False
            n_nodes = -1
            with open(fname, 'r') as f_tsp:
                for l in f_tsp:
                    if 'DIMENSION' in l:
                        n_nodes = int(l.split(' ')[-1].strip())
                    if in_sec:
                        idx, x, y = [int(w.strip()) for w in l.split(' ')]
                        coors[idx - 1] = [float(x) / 1000000.0, float(y) / 1000000.0]
                        assert len(coors) == idx
                    elif 'NODE_COORD_SECTION' in l:
                        in_sec = True
            assert len(coors) == n_nodes
            g = nx.Graph()
            g.add_nodes_from(range(n_nodes))
            nx.set_node_attributes(g, coors, 'pos')
            # api.InsertGraph(g, is_test=isValid)


if __name__=='__main__':
    print(sys.argv)
    opt = {}
    opt.update({'data_root': '../data/tsp2d', 'min_n': 15, 'max_n': 20, 'g_type': 'clustered'})
    isValid = True