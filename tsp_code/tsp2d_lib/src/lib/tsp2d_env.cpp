#include "tsp2d_env.h"
#include "graph.h"
#include <cassert>
#include <random>
#include <iostream>

int sign = 1;
double soc_ref = 0.5;
double soc_init = 0.2;


Tsp2dEnv::Tsp2dEnv(double _norm) : IEnv(_norm)
{
    // std::cout<<"Tsp2dEnv::Tsp2dEnv, _norm: "<<_norm<<std::endl;     // max_n
}

void Tsp2dEnv::s0(std::shared_ptr<Graph> _g)
{
    graph = _g;
    partial_set.clear();
    action_list.clear();
    action_list.push_back(0);
    partial_set.insert(0);

    state_seq.clear();
    state_already_list.clear();
    state_already_list.push_back(0);
    act_seq.clear();
    reward_seq.clear();
    sum_rewards.clear();
    soc = soc_init;
    soc_list.clear();    
    soc_list.push_back(soc);
    std::cout<<"\nreset"<<std::endl; 
}
double soc_norm = 300;
double Tsp2dEnv::step(int a)
{
    assert(graph);
    assert(partial_set.count(a) == 0);
    assert(a > 0 && a < graph->num_nodes);

    state_seq.push_back(action_list);
    act_seq.push_back(a);

    // std::cout<<"L44: i: "<<state_already_list.back()<<", a: "<<a<<std::endl;
    double r_t = add_node(a);
    
    reward_seq.push_back(r_t);
    sum_rewards.push_back(r_t);  

    int is_charger = get_charger_attributes(a);
    std::cout<<"soc: "<<soc<<", is_charger: "<<is_charger<<", a: "<<a<<std::endl;
    if(is_charger==1)
    {
        soc = soc_ref;
        std::cout<<"Charger node: "<<a<<"soc:"<<soc<<std::endl;
    }
    else
    {
        double distance = graph->dist[state_already_list.back()][a];
        std::cout<<"i: "<<state_already_list.back()<<", a: "<<a<<", dist:"<<distance<<std::endl;
        double soc_del = distance / soc_norm;
        soc -= soc_del;
        std::cout<<"soc_del: "<<soc_del<<", soc: "<<soc<<std::endl;
    }    
    std::cout<<"after soc_del, soc: "<<soc<<std::endl; 
    soc_list.push_back(soc);
    state_already_list.push_back(a);
    int end = graph->num_nodes;
    for (int i = 0; i < end; ++i) {
        std::cout << "tsp2d_env_soc_list[" << i << "]: " << soc_list[i] << std::endl;
    }
    std::cout<<"end:"<<end<<"in step() tsp2d_env.cpp"<<std::endl;

    return r_t;
}

int Tsp2dEnv::randomAction()
{
    assert(graph);
    avail_list.clear();

    for (int i = 0; i < graph->num_nodes; ++i)
        if (partial_set.count(i) == 0)
            avail_list.push_back(i);
    
    assert(avail_list.size());
    int idx = rand() % avail_list.size();
    return avail_list[idx];
}

bool Tsp2dEnv::isTerminal()
{
    assert(graph);
    return ((int)action_list.size() == graph->num_nodes);
}

double Tsp2dEnv::add_node(int new_node)
{
    double cur_dist = 10000000.0;
    int pos = -1;
    for (size_t i = 0; i < action_list.size(); ++i)
    {
        int adj;
        if (i + 1 == action_list.size())
            adj = action_list[0];
        else
            adj = action_list[i + 1];
        double cost = graph->dist[new_node][action_list[i]]
                     + graph->dist[new_node][adj]
                     - graph->dist[action_list[i]][adj];
        if (cost < cur_dist)
        {
            cur_dist = cost;
            pos = i;
        }
    }
    assert(pos >= 0);
    assert(cur_dist >= -1e-8);
    action_list.insert(action_list.begin() + pos + 1, new_node);
    partial_set.insert(new_node);

    // std::cout<<"norm = "<<norm<<std::endl;
    double r_t = sign * cur_dist / norm;
    if (soc <= 0.1)
    {
        r_t -= 100 * (soc_ref - soc);
    }
    return r_t;
}

int Tsp2dEnv::get_charger_attributes(int node)
{
    assert(graph);
    return graph->is_charger[node];
}