# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 10:21:25 2019

@author: 10809305
"""
import os
import shutil
import random
import pandas as pd

from fileIO import csv_path_list

def collect_roi(path):
    
    csv_list = csv_path_list(path)
    df_all = None
    for idx in range(len(csv_list)):
        print(csv_list[idx])
        df_csv = pd.read_csv(csv_list[idx], header=0, index_col=None)
        df_filter = df_csv[['kb_model', 'location' , 'description']]
        df_all = pd.concat([df_all, df_filter], axis = 0)
    
#    df_all.to_csv(os.path.join(os.path.dirname(), 'all.csv'), header = True, index = False)
    return df_all


def df_img(image_dir, df_csv):
    img_record, error_record = [], []
    columns = ['img_path', 'kb_model', 'label','location', 'description']
    i = 0
    for root, dirs, files in os.walk(image_dir):

        for file in files:
            if not file.endswith('.jpg'): continue
            _img_kb = os.path.basename(os.path.dirname(root))
            _label = os.path.basename(root)
            if '@' in file: _loc = file.split('@')[1].split('_')[0]
            else: _loc = file.split('_')[2]
            filter_kb_loc = (df_csv['kb_model'] == _img_kb) & (df_csv['location'] == _loc)
            _img_desc = df_csv[filter_kb_loc]['description'].values.tolist()

            if len(_img_desc) == 1:
                i += 1
                _img_desc = _img_desc[0]
                print('\rNum: %s , img: %s' % (i, file), end='')
                img_record.append([os.path.join(root, file), _img_kb, _label, _loc, _img_desc])
            else:
                error_record.append([file, _img_kb,  _label, _loc, len(_img_desc)])

            
    print('')
    df_error = pd.DataFrame(error_record, columns=columns)
    df_error.to_csv(os.path.join(image_dir, 'ROIerror_record.csv'), header = True, index = False)
    df_img_record = pd.DataFrame(img_record, columns=columns)

    return df_img_record

def count_list(column_str, df): # count each column 
    count_record = []
    columns = [column_str, 'count']
    all_count = df[column_str].values.tolist()
    all_count_set = set(all_count)    
    for item in all_count_set:
        count_record.append([item, all_count.count(item)])    
    df_count = pd.DataFrame(count_record, columns=columns)
    
    return df_count

def count_list_by_label(key, column_str, df): # count description by key
    all_key = df[key].values.tolist()
    all_key_set = set(all_key)
    df_key_list, df_str_key = [], []
    
    for item in all_key_set:
        _df = []
        filter_key = (df[key] == item)
        item_count = df[filter_key][column_str].values.tolist()
        item_count_set = set(item_count)
        for item1 in item_count_set:
            _df.append([item1, item_count.count(item1)])
        df_key_list.append(_df)
        df_str_key.append(item)
        
    return df_str_key, df_key_list

def get_ramdom_img(img_filter_index, each_key_num, df, save_image_dir, image_times):
    random_img_index = random.sample(img_filter_index, each_key_num)
#    print('random_idx: ' + str(random_img_index))
    for ran_idx in range(len(random_img_index)):
        _kb_model = df.iloc[random_img_index[ran_idx]]['kb_model']
        _image_path =  df.iloc[random_img_index[ran_idx]]['img_path']
        _image_name = os.path.basename(_image_path)
        _image_label = df.iloc[random_img_index[ran_idx]]['label']
        _save_image_dir = os.path.join(save_image_dir, _kb_model, _image_label)
        
        if image_times:
            _image_name = '%s_%s.jpg' % (os.path.splitext(_image_name)[0], image_times)
            _save_image_file = os.path.join(_save_image_dir, _image_name)
        else:
            _save_image_file = _save_image_dir
            
        
        if not os.path.exists(_save_image_dir):
            os.makedirs(_save_image_dir)
        if not os.path.exists(os.path.join(_save_image_dir, _image_name)):
            shutil.copy(_image_path, _save_image_file)

def get_times_img(img_filter_index, df, save_image_dir, image_times):
    for filter_idx in range(len(img_filter_index)):
        _kb_model = df.iloc[img_filter_index[filter_idx]]['kb_model']
        _image_path =  df.iloc[img_filter_index[filter_idx]]['img_path']
        _image_name = os.path.basename(_image_path)
        _image_label = df.iloc[img_filter_index[filter_idx]]['label']
        _save_image_dir = os.path.join(save_image_dir, _kb_model, _image_label)

        for times_idx in range(image_times):
            _image_times_name = '%s_%s.jpg' % (os.path.splitext(_image_name)[0], times_idx)
            if not os.path.exists(_save_image_dir):
                os.makedirs(_save_image_dir)
            if not os.path.exists(os.path.join(_save_image_dir, _image_times_name)):
                shutil.copy(_image_path, os.path.join(_save_image_dir, _image_times_name))

def get_balance_img(key, column_str, key_list_idx, df, save_image_dir):
    error_record = []
    columns = [column_str, 'count']
    key_num = len(key_list_idx)
    df_key = pd.DataFrame(key_list_idx, columns=columns)
#    key_image_num = int(df_key['count'].sum())
    if key == 'OK':
        each_key_num = int(df_key['count'].median())
    else:
        each_key_num = int(df_key['count'].mean())
    #each_key_num = 50

    print('each_key_num: ' + str(each_key_num) + '; desc_num: ' + str(len(key_list_idx)))

    for key_idx in range(key_num):
        filter_key = ((df[column_str] == df_key[column_str][key_idx]) 
                                            & (df['label'] == key))
        img_filter = df[filter_key]
        img_filter_index = img_filter.index.values.tolist()

        if len(img_filter) >= each_key_num:
            if key == 'OK' :
                get_ramdom_img(img_filter_index, each_key_num, df, save_image_dir, 0)
            else:
                get_ramdom_img(img_filter_index, len(img_filter), df, save_image_dir, 0)
                
            print(key_idx, '/', key_num,'count: ' + str(len(img_filter_index)))
            
        else:
            try:
                _image_times = int(each_key_num / len(img_filter_index))
                _image_remainder = int(each_key_num % len(img_filter_index))
            except:
                _image_times = 0
                _image_remainder = 0
                print('No img, label: ', key, ' desc:', df_key[column_str][key_idx])
                error_record.append([key, df_key[column_str][key_idx]])  
            
            print(key_idx, '/', key_num,'count: ' + str(len(img_filter_index)) + '  times: ' + str(_image_times) + '  remainder: ' + str(_image_remainder))
            get_times_img(img_filter_index, df, save_image_dir, _image_times)        
            if _image_remainder :
                get_ramdom_img(img_filter_index, _image_remainder, df, save_image_dir, _image_times)
            else: pass
    fp_w = open(os.path.join(save_image_dir, 'balance_result.txt'), 'a+')
    fp_w.write(str(key) +' each_key_num: ' + str(each_key_num) + '; desc_num: ' + str(len(key_list_idx)) + '\n')
    fp_w.close()
    df_error = pd.DataFrame(error_record, columns = ['label', 'discription'])
    df_error.to_csv(os.path.join(save_image_dir, 'img_error_record.csv'), header = True, index = False)
    df_key.to_csv( os.path.join(save_image_dir, '%s_count.csv' % key), header = True, index = False)
    
    

def balance_by_desciption(image_dir, save_image_dir, csv_path):


    
    df_csv = collect_roi(csv_path)
#    print(len(df_csv))
    df_img_record = df_img(image_dir, df_csv)   
    df_desc_label, df_label_list = count_list_by_label('label', 'description', df_img_record)
    for i in range(len(df_desc_label)):
        print('label: ', df_desc_label[i], 'desc: ', len(df_label_list[i]))
    
    
# =============================================================================
#     
#     #-----all image parameter
#     df_desc_count = count_list('description', df_img_record)
#     
#     tatol_image_num = len(df_img_record)
#     total_location_num = len(df_desc_count)
#     print(tatol_image_num)
#     print(total_location_num)
# =============================================================================
    
    for idx in range(len(df_label_list)):
        if df_desc_label[idx] == 'OK':
            print(df_desc_label[idx])
            get_balance_img('OK', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'NG':
            print(df_desc_label[idx])
            get_balance_img('NG', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'UNCONFIRMED':
            print(df_desc_label[idx])
            get_balance_img('UNCONFIRMED', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'MISS':
            print(df_desc_label[idx])
            get_balance_img('MISS', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'POOR':
            print(df_desc_label[idx])
            get_balance_img('POOR', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'SHIFT':
            print(df_desc_label[idx])
            get_balance_img('SHIFT', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'WRONG':
            print(df_desc_label[idx])
            get_balance_img('WRONG', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'SHORT':
            print(df_desc_label[idx])
            get_balance_img('SHORT', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'SHIFT1':
            print(df_desc_label[idx])
            get_balance_img('SHIFT1', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'SHIFT2':
            print(df_desc_label[idx])
            get_balance_img('SHIFT2', 'description', df_label_list[idx], df_img_record, save_image_dir)
        elif df_desc_label[idx] == 'EMPTY':
            print(df_desc_label[idx])
            get_balance_img('EMPTY', 'description', df_label_list[idx], df_img_record, save_image_dir)
        else:
            print('other label: ' + str(df_desc_label[idx]))
            
    df_img_record.to_csv( os.path.join(save_image_dir, 'img_count.csv'), header = True, index = False)


if __name__ == '__main__':   
    image_dir = r'/media/swpcserver/DISK2/Hazel/MultiClass/P1_MergeP3poor/datasets2'
    save_image_dir = r'/media/swpcserver/DISK2/Hazel/MultiClass/P1_MergeP3poor/balance'
    csv_path = r'/media/swpcserver/DISK2/Hazel/MultiClass/P1_MergeP3poor/ROI' 
    balance_by_desciption(image_dir, save_image_dir, csv_path)

