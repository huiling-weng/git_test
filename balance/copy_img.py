# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 13:51:07 2020

@author: 10809305
"""

import os
import shutil

def only_label(path, label, save_dir):
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if not file.endswith('.jpg'): continue
            _img_kb = os.path.basename(os.path.dirname(root))
            _label = os.path.basename(root)
            img_path = os.path.join(root, file)
            if _label == label:
                save_path = os.path.join(save_dir, _img_kb, _label)
                os.makedirs(save_path, exist_ok=True)
                if not os.path.exists(os.path.join(save_path, file)):
                    shutil.copy(img_path, save_path)
                    print('copy: ', file)
                


path = r'D:\P1_image\C_Others\From_p1_database\L'
save_dir = r'D:\P1_image\C_Others\temp'
only_label(path, 'NG', save_dir)