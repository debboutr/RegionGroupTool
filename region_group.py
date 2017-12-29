#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 20:05:57 2017
    
gdal_rasterize -a DRAWSEQ -tr 90.0 90.0 -l states  -co "COMPRESS=LZW" -a_nodata 0 -ot UInt32 /home/rick/projects/RegionGroupTool/states.shp /home/rick/projects/RegionGroupTool/states.tif

TODO: add table for matchup!
TODO: test ortho connectivity
TODO: add check for dtype INT
    
@author: rick
"""
import numpy as np
import rasterio as rs
from scipy.ndimage import label, generate_binary_structure

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

def region_group(geo_raster, zone_connectivity=True):
    NDV = data.nodata
    final = np.zeros(data.shape)
    array = data.read(1)
    values = np.delete(np.unique(array), NDV)
    if zone_connectivity:
        s = generate_binary_structure(2,2)
    incrementor = 0 # TODO: how should new values be generated???
    for val in values:
        single = array.copy()
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
    
20295 * 29689
        
  25975  * 11375    
         
        
        profile['dtype']
type(rs.uint32)



#########################################################################    
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