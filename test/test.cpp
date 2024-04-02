#include <iostream>
#include <vector>


int main(){
    unsigned int batch_size = 6;
    unsigned int max_n = 10;
    std::vector< std::vector<double>* > list_pred;
    list_pred.resize(batch_size);
    for (unsigned int i = 0; i < batch_size; ++i)
        list_pred[i] = new std::vector<double>(max_n+10);
    
    for (unsigned int i = 0; i < batch_size; ++i){
        // std::cout<<list_pred[i]->data()<<std::endl;
        std::cout<<*(list_pred[i]->data())<<std::endl;
    }
    return 0;
}

