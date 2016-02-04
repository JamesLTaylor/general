#this is a cython wrapper on C functions to call them in python


cdef extern from "puzzleFunctions.h":
    int TemplateMatch_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result)
    int TemplateMatch_V_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result)
    int TemplateMatch_C_fast(int* img, int rowsImg, int colsImg, int* templateImg, int* mask, int rowsTpl, int colsTpl, int* result);
