#include <iostream>
#include <vector>
#include <glog/logging.h>
using namespace std;

int main(){
    unsigned int batch_size = 6;
    unsigned int max_n = 10;
    std::vector< std::vector<double>* > list_pred;
    list_pred.resize(batch_size);
    for (unsigned int i = 0; i < batch_size; ++i)
        list_pred[i] = new std::vector<double>(max_n+10);
    
    for (unsigned int i = 0; i < batch_size; ++i){ 
        std::cout<<*(list_pred[i]->data())<<std::endl;
    }
    auto& cur_pred = *(list_pred[2]);
    cout<<cur_pred[2]<<endl;
    cur_pred[2] = 8;
    cout<<cur_pred[2]<<endl;
    cout<<&cur_pred[2]<<endl;
    std::cout<<&list_pred[2][2]<<std::endl;
    std::cout<<list_pred[2]->data()<<std::endl;

    // for (int i = 0; i < batch_size; ++i){
    //     cout<<i<<endl;
    //     if (i >= 3){
    //         cout<<"i == 3"<<endl;
    //         break;
    //     }
    // }

 
  
    google::InitGoogleLogging("./tstlog"); //初始化 glog
    LOG(INFO) << "Hello,GOOGLE!";
 

    return 0;
}

