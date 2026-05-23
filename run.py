import os
import shutil
import subprocess


items = os.listdir('/media/yan1/liangjie/mvs_traditional/correct_data/')

def build():
    os.system('rm -rf CMakeCache.txt')
    os.system('cmake .')
    os.system('make')

def run(data_source, output_path):
    os.system('./HFPMVS ' + data_source + ' ' + output_path)
    

def quantity(output_path, quantity_objs):
    root_path = output_path + '/HFP-MVS/HFPMVS/'
    root_path3 = output_path + 'HFPMVS_Joint/'
    root_path2 = output_path + 'HFPMVS_Planar/'
    root_path1 = output_path + 'HFPMVS_Geom/'
    
    for item in quantity_objs:
        os.system('node /mvs_traditional/tool/depth2Img.js ' + root_path + ' ' + item)
    
def val(output_path, ground_root):
    input_path = output_path + "/HFPMVS/HFPMVS_model.ply"
    ground_path = ground_root + "/dslr_scan_eval/scan_alignment.mlp"
    
    cmd = "sudo " + val_path + "ETH3DMultiViewEvaluation "
    cmd += "--reconstruction_ply_path " + input_path + " "
    cmd += "--ground_truth_mlp_path " + ground_path + " "
    cmd += "--tolerances 0.01,0.02,0.05,0.1,0.2,0.5"
    
    out = os.popen(cmd)
    
    log('val', out.read(), output_path)

def remove(remove_objs, output_path):   
    root_path = output_path + 'HFPMVS/'
    
    for first_item in os.listdir(root_path):
        cur_path = root_path + first_item + '/'
        
        for remove_item in remove_objs:
            remove_path = cur_path + remove_item
            
            if os.path.isfile(remove_path):
                os.remove(remove_path)

def copyCode(output_path):
    write_path = output_path + 'code/'
    
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        
    if not os.path.exists(write_path):
        os.mkdir(write_path)

    code_lists = ['HFPMVS.cpp', 'HFPMVS.cu', 'HFPMVS.h', 'CMakeLists.txt', 'main.cpp', 'main.h', 'HFPMVS', 'run.py']
    
    for item in code_lists:
        shutil.copy('./' + item, write_path)

def copyData(source_path, target_path):
    # cmd = "rsync -av --exclude='HFPMVS_model.ply' --exclude='depths_prior.dmb' --exclude='depths_prior.png' --exclude='depths_geom.png' --exclude='dir_to_exclude2' " + source_path + " " + target_path
    cmd = "rsync -av --exclude='log' --exclude='HFPMVS_model.ply' --exclude='depths_prior.dmb' --exclude='*.png' --exclude='dir_to_exclude2' " + source_path + " " + target_path
    
    os.system(cmd)
    
def log(target, describle, output_path):
    log_path = output_path + 'log/'
    target_path = log_path + target + '.txt'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
        
    if not os.path.exists(log_path):
        os.mkdir(log_path)
        
    output = subprocess.check_output(['ls', '-l'])
    output = output.decode('utf-8')
    
    with open(target_path, 'a') as f:
        print(describle, file = f)     
        
import os
import smtplib


# over_items = ["meadow", "office", "delivery_area", "playground"]
# over_items = ['meadow', 'delivery_area']
items = ['']
geom_changed = ['0.02']
over_items = []
 
# 使用普通的平面先验
for data_item in items:
    output_path = '/segment-anything-main/notebooks/VRU_gz/HFP-MVS/'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    # output_path += data_item + '/'
    
    # os.environ['GEOM_CHANGED'] = geom_ratio
    over_flag = False
    for over_item in over_items:
        if over_item == data_item:
            over_flag = True
            break
    
    if over_flag:
        continue
    
    quantity_objs = ['depths_geom', 'depths_prior', 'plane_masks']
    remove_objs = ['normals.dmb', 'costs.dmb', 'depths.dmb', 'depths_prior.dmb']

    data_source = '/data2/lj/VRU_gz/'
    val_path = '/media/yan1/liangjie/mvs_traditional/multi-view-evaluation-master/'
    ground_root = '/data1/lj/ground_truth/' + data_item + '/'  
    
    base_data_path = '/data1/lj/832/1biggerBase/' + data_item + '/HFPMVS'
    # print("base_data_path: ", base_data_path)

    # build()
    # copyCode(output_path)
    # if not os.path.exists(output_path):
    #     os.mkdir(output_path)
    # if not os.path.exists(output_path + '/HFPMVS'):
    #     os.mkdir(output_path + '/HFPMVS')
    # if not os.path.exists(output_path + '/HFPMVS_Joint'):
    #     os.mkdir(output_path + '/HFPMVS_Joint')
    # if not os.path.exists(output_path + '/HFPMVS_Planar'):
    #     os.mkdir(output_path + '/HFPMVS_Planar')
    # if not os.path.exists(output_path + '/HFPMVS_Geom'):
    #     os.mkdir(output_path + '/HFPMVS_Geom')
    # os.system("sudo rm -rf " + output_path + '/HFPMVS')
    # copyData(base_data_path, output_path + '/')
    run(data_source, output_path)
    # val(output_path, ground_root)
    # os.system("sudo node /media/yan1/liangjie/mvs_traditional/tool/depth2ImgS.js")
    quantity(output_path, quantity_objs)
    # send_email_with_attachments(output_path)
    # print("over")
    # print('quantity over...')
    # remove(remove_objs, output_path)
    # print("remove over...")

