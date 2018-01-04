#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 20:05:57 2017
    
gdal_rasterize -a DRAWSEQ -tr 90.0 90.0 -l states  -co "COMPRESS=LZW" -a_nodata 0 -ot UInt32 /home/rick/projects/RegionGroupTool/states.shp /home/rick/projects/RegionGroupTool/states.tif

TODO: gonna need to be able to window
TODO: add table for matchup!
TODO: test ortho connectivity
TODO: add check for dtype INT
    
@author: rick
"""
import numpy as np
import rasterio as rs
from rasterio.windows import Window
from scipy.ndimage import label, generate_binary_structure

def fix_max(a,i,d):          
    nums = list(np.unique(a)[1:])
    nums.sort(reverse=True)          
    for num in nums: #sorted return for covering NDV 0
        if num not in d.keys():
            a[a==num] = (i+1)
            i += 1
    return a   

def equal(m,n):
    if m==n:
        return True
    else:
        return False
    
def get_connect(a,b):
    out = {}
    assert(len(a)==len(b))
    uni = np.where(a!=NDV)[0]
    for i in uni:
        if a[i] in out.keys():
            continue
        if i == 0:
            win = range(i,i+2) 
        elif i == len(a):
            win = range(i-1,i+1)
        else:
            win = range(i-1,i+2)
        for j in win :        
            if equal(a[i],b[j]) and not a[i] in out.keys():
                out[a[i]] = (i,j)
    return out

# make windows
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

def region_group(data, zone_connectivity=True):
    final = np.zeros(data.shape)
    values = np.delete(np.unique(data), NDV)
    if zone_connectivity:
        s = generate_binary_structure(2,2)
    incrementor = 0 # TODO: how should new values be generated???
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
# TODO: negative index of b in get_connect    
    
    with rs.open('og.tif') as data:
        profile = data.profile
#        with rs.open('rio_carol.tif', 'w', **profile) as dst:
#        print data.shape
        NDV = data.nodata
        windows = make_windows(data.shape[1],4)
        arr_max = 0
        c_orig = []
        idx = {}
        for win in windows:
            arr = data.read(window=win)[0]
#            break
            print(arr.shape)
#            get matching vals
            if len(c_orig) > 0: # they won't be the same values in new, needs to be tracked somehow
                c_next = arr[:,0]
                idx = get_connect(c_orig,c_next)
            print(idx)
            c_orig = arr[:,-1]
            print('**********')
#            print(len(c_orig))
            new = region_group(arr) 
            print(np.unique(new))
            print('Arrays new/old')            
            if arr_max > 0:
                print(arr_max)
                np.place(new, new!=NDV, new[new!=NDV]+arr_max)
#                new = fix_max(new,arr_max,idx)
            print(new.max())
            print(np.unique(new))
            if idx: #this isn't working
                for val in idx: # get value @ index in the old arr, then val at that index in new, that's what we want to replace
                    new_idx = idx[val][1]
                    new_fin = new[:,0]
                    old = new_fin[new_idx]
                    np.place(new, new==old, val)
            print(new.max())
            print('**********')
            c_new = new[:,-1]
            arr_max = new.max()
#            arr_max += len(np.unique(new)) - len(idx)#new.max()
            print(np.unique(new))
#            print(len(idx))
            print('**********')
            print('**********')
            
# go to new, get the zeroeth column and grab the new value, build a new dict          
 
        
#win = (0,None),(0,300)
#d = data.read(window=win)
#c=d[0]
#old_check = c[:,-1]
#new = region_group(c)
#np.unique(new)
        
    
    
    
        dst.write(new.astype(rs.uint32),1)   
    
    
    with rs.open('carol.tif') as data:    
        new = region_group(data)
        np.unique(new)
        profile = data.profile
    
    
    with rs.open('rio_carol.tif', 'w', **profile) as dst:
        dst.write(new.astype(rs.uint32),1)        
        

profile['dtype']
type(rs.uint32)



#resolve num_windows to math output

make_windows(5311,3)
Window(col_off, row_off, width, height)
######################################################################### 
# window vertically, hold the last dim of orig values to compare w/
# the new windows first to link values. Get the value of point where that's 
# true after increasing vals in new window, then you'll have to have held 
# on to the 'grouped' value from the previous window as well. So, both the 
# orig and final array (x[:,-1]) will have to be held to update to the new 
# window where there are new connections
arr = np.arange(81).reshape(27,3)
a = np.array([0, 4, 5, 0]*6).reshape(8,3)
b = np.array([4, 5, 0, 0]*6).reshape(8,3)
np.hstack([a,b])
c = a[:,-1]
d = b[:,0]
NDV = 0
# get index of array d that has matching val in window of c, for connection
for idx, val in np.ndenumerate(d):
    if val == NDV:
        continue
    x = idx[0]
    if x == 0:
        win = [x,x+1]
    elif x == (len(d)-1):
        win = [x-1, x]
    else:
        win = [x-1,x,x+1]
    if val in c[win]:       
        print (x, val)

# TODO: (a) hold last column of windowed array of both (1)before and (2)after label        
# TODO: get indexes of where there is a match in (a1), then get value of those in (a2)
# TODO: 



get_connect(c,d)


    
x = np.array([[2,1,1,2,2],
              [0,1,1,0,3],
              [1,2,2,3,1]])

# try to raise value of array by max of the previous for windowing
y = x.copy()
z = x.copy()
np.place(y, y>0, y[y>0]+x.max())
np.place(z, z>0, z[z>0]+y.max())

   
#import numpy as np
#import georasters as gr
#from scipy.ndimage import label, generate_binary_structure
#
#def replace(arr, inc_val, no_data):
#    '''
#    replaces arr values in-place with inc_val
#    '''
#    fin = arr.copy()
#    uni_arr = np.delete(np.unique(arr), no_data)
#    for num in uni_arr: 
#        a = fin.copy()
#        iso = a != num
#        a[iso] = no_data 
#        np.place(a, a==num, (num + inc_val))
#        np.copyto(arr,a, where=a!=no_data)
#
#def region_group(geo_raster, zone_connectivity=True):
#    NDV = geo_raster.nodata_value
#    final = np.zeros(geo_raster.raster.data.shape)
#    values = np.delete(np.unique(geo_raster.raster.data), NDV)
#    if zone_connectivity:
#        s = generate_binary_structure(2,2)
#    incrementor = 0 # TODO: how should new values be generated???
#    for val in values:
#        single = geo_raster.raster.data.copy()
#        isolate = single != val
#        single[isolate] = NDV
#        grouped, num_feats = label(single, 
#                                   structure=s if zone_connectivity else None)    
#        if incrementor > 0:
#            replace(grouped, incrementor, NDV)
#        incrementor += num_feats
#        np.copyto(final,grouped, where=grouped!=NDV)
#    
#    return gr.GeoRaster(final,orig.geot, 
#                        nodata_value=geo_raster.nodata_value, 
#                        projection=geo_raster.projection, 
#                        datatype=geo_raster.datatype)
#
#if __name__ == '__main__':
#    
#    orig = gr.from_file('carol.tif')
#    out = region_group(orig)
#    out.to_tiff('new_carol')
######################################################################

#
#NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info('og.tif')
#np.delete(np.unique(final), NDV)

#x = np.array([[0,0,0,2,2],
#              [0,0,0,0,0],
#              [0,2,2,0,0]])
#
#x = np.array([[2,1,1,2,2],
#              [0,1,1,0,3],
#              [1,2,2,3,1]])
    
#    NDV = 0
#    final = np.zeros(x.shape)
#    values = np.delete(np.unique(x), NDV)
#    if zone_connectivity:
#        s = generate_binary_structure(2,2)
#    incrementor = 0 # TODO: how should new values be generated???
#    for val in values:
#        single = x.copy()
#        isolate = single != val
#        single[isolate] = NDV
#        grouped, num_feats = label(single, 
#                                   structure=s if zone_connectivity else None)    
#        if incrementor > 0:
#            replace(grouped, incrementor, NDV)
#        incrementor += num_feats
#        np.copyto(final,grouped, where=grouped!=NDV)