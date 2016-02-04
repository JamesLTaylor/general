#this is a cython wrapper on C functions to call them in python

import numpy as np
cimport numpy as np
from libc.stdlib cimport *
from cPuzzleFunctions cimport *

np.import_array()

def template_match(img, template, mask):

    cdef np.ndarray[np.float_t, ndim=2] c_img
    cdef np.ndarray[np.float_t, ndim=2] c_template
    cdef np.ndarray[np.float_t, ndim=2] c_mask
    cdef np.ndarray[np.float_t, ndim=2] c_result
    
    (rowsImg, colsImg) = img.shape
    (rowsTpl, colsTpl) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    
    c_img = np.ascontiguousarray(img, dtype=np.float)    
    c_template = np.ascontiguousarray(template, dtype=np.float)
    c_mask = np.ascontiguousarray(mask, dtype=np.float)
    c_result = np.ascontiguousarray(result, dtype=np.float)
    
    #print(c_mask)
    
    r = TemplateMatch_C(<double*> c_img.data, rowsImg, colsImg, <double*> c_template.data, <double*> c_mask.data, rowsTpl, colsTpl, <double*> c_result.data)
    return c_result
    
def template_match_v(img, template, mask):

    cdef np.ndarray[np.float_t, ndim=2] c_img
    cdef np.ndarray[np.float_t, ndim=2] c_template
    cdef np.ndarray[np.float_t, ndim=2] c_mask
    cdef np.ndarray[np.float_t, ndim=2] c_result
    
    (rowsImg, colsImg) = img.shape
    (rowsTpl, colsTpl) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    
    c_img = np.ascontiguousarray(img, dtype=np.float)    
    c_template = np.ascontiguousarray(template, dtype=np.float)
    c_mask = np.ascontiguousarray(mask, dtype=np.float)
    c_result = np.ascontiguousarray(result, dtype=np.float)
    
    #print(c_mask)
    
    r = TemplateMatch_V_C(<double*> c_img.data, rowsImg, colsImg, <double*> c_template.data, <double*> c_mask.data, rowsTpl, colsTpl, <double*> c_result.data)
    return c_result    
    
def template_match_fast(img, template, mask):
    
    cdef np.ndarray[np.int32_t, ndim=2] c_img
    cdef np.ndarray[np.int32_t, ndim=2] c_template
    cdef np.ndarray[np.int32_t, ndim=2] c_mask
    cdef np.ndarray[np.int32_t, ndim=2] c_result
    
    (rowsImg, colsImg) = img.shape
    (rowsTpl, colsTpl) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    
    c_img = np.ascontiguousarray(img, dtype=np.int32)    
    c_template = np.ascontiguousarray(template, dtype=np.int32)
    c_mask = np.ascontiguousarray(mask, dtype=np.int32)
    c_result = np.ascontiguousarray(result, dtype=np.int32)
    
    r = TemplateMatch_C_fast(<int*> c_img.data, rowsImg, colsImg, <int*> c_template.data, <int*> c_mask.data, rowsTpl, colsTpl, <int*> c_result.data)
    return c_result