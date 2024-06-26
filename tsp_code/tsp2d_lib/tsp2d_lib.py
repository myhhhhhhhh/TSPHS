import ctypes
import networkx as nx 
import os
import sys

class Tsp2dLib(object):

    def __init__(self, args):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # print(dir_path)
        self.lib = ctypes.CDLL('%s/build/dll/libtsp2d.so' % dir_path)
        self.lib.Fit.restype = ctypes.c_double
        self.lib.Test.restype = ctypes.c_double
        self.lib.GetSol.restype = ctypes.c_double
        arr = (ctypes.c_char_p * len(args))()
        # print(args)
        # print(type(args))
        # arr[:] = args
        for i, arg in enumerate(args):
            arr[i] = arg.encode()
        self.lib.Init(len(args), arr)
        self.ngraph_train = 0
        self.ngraph_test = 0

    def __CtypeNetworkX(self, g):
        coors = nx.get_node_attributes(g, 'pos')
        n = len(coors)
        coor_x = (ctypes.c_double * n)()
        coor_y = (ctypes.c_double * n)()

        for i in range(n):
            coor_x[i], coor_y[i] = coors[i]
        
        # charger information 
        chargers = nx.get_node_attributes(g, 'isCharger')
        is_charger = (ctypes.c_int * n)()
        for i in range(n):
            is_charger[i] = chargers[i]
            
        return (n, ctypes.cast(coor_x, ctypes.c_void_p), ctypes.cast(coor_y, ctypes.c_void_p), 
                ctypes.cast(is_charger, ctypes.c_void_p) )

    def TakeSnapshot(self):
        self.lib.UpdateSnapshot()

    def ClearTrainGraphs(self):
        self.ngraph_train = 0
        self.lib.ClearTrainGraphs()

    def InsertGraph(self, g, is_test):
        n_nodes, coor_x, coor_y, is_charger = self.__CtypeNetworkX(g)
        if is_test:
            t = self.ngraph_test
            self.ngraph_test += 1
        else:
            t = self.ngraph_train
            self.ngraph_train += 1

        self.lib.InsertGraph(is_test, t, n_nodes, coor_x, coor_y, is_charger)
    
    def LoadModel(self, path_to_model):
        p = ctypes.cast(path_to_model, ctypes.c_char_p)
        self.lib.LoadModel(p)

    def SaveModel(self, path_to_model):
        p = path_to_model.encode('utf-8')
        p = ctypes.cast(p, ctypes.c_char_p)
        # print('p:', p)
        self.lib.SaveModel(p)

    def GetSol(self, gid, maxn):
        sol = (ctypes.c_int * (maxn + 10))()
        sol_state_already_list = (ctypes.c_int * (maxn + 10))()
        soc_list = (ctypes.c_double * (maxn + 10))()
        val = self.lib.GetSol(gid, sol, sol_state_already_list, soc_list)
        return val, sol, sol_state_already_list, soc_list

if __name__ == '__main__':
    f = Tsp2dLib(sys.argv)
    print("end")
