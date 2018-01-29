#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 20:05:57 2017
    
('gdal_rasterize -a DRAWSEQ -tr 90.0 90.0 -l states  -co "COMPRESS=LZW" '
'-a_nodata 0 -ot UInt32 /home/rick/projects/RegionGroupTool/states.shp '
'/home/rick/projects/RegionGroupTool/states.tif')

TODO: gonna need to be able to window
TODO: add table for matchup!
TODO: test ortho connectivity
TODO: add check for dtype INT

Schema:
    - get window
    - hold -1 column to match vals across windows
    - create new values
    - add matches to link_list
    - tricky: how to apply new values into windows so we don't trip on matches 
                returned from region_group function
@author: rick
"""
import numpy as np
import pandas as pd
import rasterio as rs
from collections import defaultdict
#from rasterio.windows import Window
from scipy.ndimage import label, generate_binary_structure

def get_connections(a,b):
    start = 0
    changes = np.append(np.where(np.diff(a) != 0)[0]+1,len(a)-1)
    keepers = defaultdict(list)
    for stop in changes:
#        print start,stop
        value = a[start] # value being tracked
        if value == NDV:
#            print 'NDV'
            start = stop
            continue
        for idx in range(start,stop): # iter all indexes of val
            idxs = np.array(range(idx-1,idx+2)) # 3-cell window
            idxs = idxs[idxs>=0] # remove negative idx from 0
            same = np.where(b[idxs]==value)[0] # matches a | b
            if same.any():
                # appending list to key will allow for >1 index of same val
                keepers[value].append((idx,idxs[same[0]])) #idx of 1st match val
                break
        start = stop
    return keepers

def make_windows(arr_len, num_win):
    i, wins = 0, []
    width = arr_len/num_win
    while i<arr_len:
        wins.append(((0,None),(i,i+width if (i+width)<arr_len else None)))
        i+=width
    return wins

def replace(arr, inc_val, no_data):
    '''
    replaces arr values in-place with inc_val
    '''
    fin = arr.copy()
    uni_arr = np.delete(np.unique(arr), no_data)
    for num in uni_arr: 
        a = fin.copy()
        iso = a != num
        a[iso] = no_data 
        np.place(a, a==num, (num + inc_val))
        np.copyto(arr,a, where=a!=no_data)

def region_group(data, incrementor=0, zone_connectivity=True):
    final = np.zeros(data.shape,dtype=int)
    values = np.delete(np.unique(data), NDV)
    if zone_connectivity:
        s = generate_binary_structure(2,2)
    for val in values:
        single = data.copy()
        isolate = single != val
        single[isolate] = NDV
        grouped, num_feats = label(single, 
                                   structure=s if zone_connectivity else None)    
        if incrementor > 0:
            replace(grouped, incrementor, NDV)
        incrementor += num_feats
        np.copyto(final,grouped, where=grouped!=NDV)
    
    return final

if __name__ == '__main__':
    
    with rs.open('og.tif') as data:
#        data = rs.open('og.tif')
        profile = data.profile
        with rs.open('rio_carol.tif', 'w', **profile) as dst:
            NDV = data.nodata # ??? make this int
            windows = make_windows(data.shape[1],4)
            c_orig = []
            idx = {}
            old_col_vals = []
            link  = defaultdict(list)
            incrementor = 0
    # Can likely refactor from here???                
            for win in windows:
                arr = data.read(window=win)[0]
                # get matching vals
                if len(c_orig) > 0: # flag every arr after the first
                    c_next = arr[:,0] # get original values in first column
                    connect_dict = get_connections(c_orig,c_next) # retain orig vals and idxs
                c_orig = arr[:,-1] # replace for next get_connect comparison
                new = region_group(arr, incrementor) # make new groups
                # get old value as key with new[:,0] index as value
                if len(old_col_vals)>0 and len(connect_dict)>0:
                    for connection in connect_dict.items():
                        connection_idxs = connection[1]
                        for indexes in connection_idxs:
                            old_val = old_col_vals[indexes[0]]
                            replace_val = new[:,0][indexes[1]]
                            np.place(new,new==replace_val,old_val)
                print(np.unique(new))                  
                # match vals for link table
                new_vals = np.unique(new)
                for new_val in np.delete(new_vals,NDV): 
                    item_idx = np.where(new==new_val)
                    old_val = arr[item_idx[0][0]][item_idx[1][0]]
                    if not any(new_val in e for e in link.values()):
                        link[old_val].append(new_val)
                old_col_vals = new[:,-1]
                incrementor = new.max()
                print('**********')
                dst.write(new.astype(np.int32), indexes=1, window=win)
    link_table = pd.DataFrame([(h[0],j) for h in link.items() for j in h[1]], columns=['original_value','group_value'])
    link_table.to_csv('link_table.csv',index=False)
#win = windows[0]
#win = windows[1]
#win = windows[2]
#win = windows[3]
#win = windows[4]