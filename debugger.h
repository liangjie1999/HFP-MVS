#ifndef _DEBUGGER_H_
#define _DEBUGGER_H_

#include <chrono>
#include <iostream>
#include <fstream>
#include <assert.h>
#include <map>
#include "main.h"

using namespace std;

typedef struct Stage {
    float time_avg;
    int time_num;
} Stage;

class Debugger {
public:
    void s(string t);
    void e();
    void set_log_path(string log_path);
    void log_stat_time();

    // 获取单例对象的静态方法
    static Debugger& getInstance() {
        static Debugger instance; // 局部静态变量，只会被创建一次
        return instance;
    }

    std::string cost_path;
    float* cost_cuda = nullptr;
    float* cost_host = nullptr;
    bool debug = false;

    // 创建存放cost_device和cost_host的空间
    int createCostSpace(int r, int c, int cn, std::string path);
    int destoryCostSpace();
    // 先所有的depth 然后是所有的cost
    // 0 -- before 1 -- up_near, 2 -- up_far, 3 -- down_near, 4 -- down_far, 5 -- left_near, 6 -- left_far, 7 -- right_near, 8 -- right_far
    int writeCostDmb();
    int beginDebug();
    int endDebug();

private:
    bool state = false;
    std::chrono::steady_clock::time_point start;
    string tips;
    string out_path;
    string stat_path;
    ofstream out;
    ofstream stat;

    map<string, Stage> time_result;    

    int rows;
    int cols;
    int cost_num;
    int cost_count = 0;
    Debugger() {
        cost_cuda = nullptr;
        cost_host = nullptr;
    }
    Debugger(const Debugger&) = delete;
    Debugger& operator=(const Debugger&) = delete;
};

#endif