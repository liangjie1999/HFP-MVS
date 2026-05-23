#include "./debugger.h"

void Debugger::set_log_path(string log_path) {
    out_path = log_path + "/time_middle.txt";
    stat_path = log_path + "/time_stat.txt";
}

void Debugger::s(string t) {
    state = true;
    tips = t;

    cout << "Begin: " << tips << endl;
    start = std::chrono::steady_clock::now();
}

void Debugger::e() {
    if(state == false) {
        assert(false);
    }

    state = false;
    std::chrono::steady_clock::time_point end = std::chrono::steady_clock::now();
    cout << "End: " << tips << endl;

    out.open(out_path, ios::app);
    // out << "-----------" << endl << tips << endl; 
    // out << "Work took: "
    //     << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
    //     << " microseconds\n";
    // out << "Work took: "
    //     << std::chrono::duration_cast<std::chrono::seconds>(end - start).count()
    //     << " seconds\n";
    
    out << tips << " " << (float)std::chrono::duration_cast<std::chrono::microseconds>(end - start).count() / 1000000 << endl;

    
    if(time_result.find(tips) == time_result.end()) {
        Stage stage;
        stage.time_avg = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
        stage.time_num = 1;
        time_result.insert(pair<string, Stage>(tips, stage));
    } else {
        std::cout << (time_result.find(tips) -> first) << std::endl;
        Stage stage = time_result.find(tips) -> second;
        stage.time_avg = (stage.time_avg * stage.time_num + std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()) / (stage.time_num + 1);
        stage.time_num = stage.time_num + 1;
    }
    
    // out << "-----------" << endl << endl;

    out.close();
}

void Debugger::log_stat_time() {
    stat.open(stat_path, ios::app);

    // 遍历HashMap
    float total_time = 0;
    for(auto i = time_result.begin(); i != time_result.end(); ++i) {
        string stage_name = i -> first;
        Stage stage = i -> second;
        stat << stage_name << ": " << stage.time_avg << endl;
        total_time += stage.time_avg; 
    }

    stat << "total: " << total_time << endl;
    stat.close();
}

int Debugger::writeCostDmb() {
    cudaMemcpy(cost_host, cost_cuda, sizeof(float) * rows * cols * cost_num * 2, cudaMemcpyDeviceToHost);

    FILE *outimage;
    std::string current_cost_path = cost_path + "/cost" + std::to_string(cost_count++) + ".dmb";
    outimage = fopen(current_cost_path.c_str(), "wb");

    if (!outimage) {
        std::cout << "Error opening file " << current_cost_path << std::endl;
    }
    
    // 10 cost
    int32_t type = 10;
    int32_t h = rows;
    int32_t w = cols;
    int32_t nb = cost_num * 2;

    fwrite(&type,sizeof(int32_t),1,outimage);
    fwrite(&h,sizeof(int32_t),1,outimage);
    fwrite(&w,sizeof(int32_t),1,outimage);
    fwrite(&nb,sizeof(int32_t),1,outimage);

    int32_t datasize = w * h *nb;
    fwrite(cost_host, sizeof(float), datasize, outimage);

    fclose(outimage);

    return 0;
}

int Debugger::createCostSpace(int r, int c, int cn, std::string path) {
    // cost_num: 9
    if (cost_host != nullptr) {
        delete[] cost_host;
    }
    if (cost_cuda != nullptr) {
        cudaFree(cost_cuda);
    }

    rows = r;
    cols = c;
    cost_num = cn;
    cost_path = path;
    std::cout << r << "," << c << "," << cn << std::endl;
    std::cout << r * c * cn * 2 << std::endl;
    cost_host = new float[r * c * cn * 2];
    cudaMalloc((void **)&cost_cuda, sizeof(float) * r * c * cn * 2);

    return 0;
}

int Debugger::destoryCostSpace() {
    if (cost_host != nullptr) {
        delete[] cost_host;
        cost_host = nullptr;
    }

    if (cost_cuda != nullptr) {
        cudaFree(cost_cuda);
        cost_cuda = nullptr;
    }

    return 0;
}