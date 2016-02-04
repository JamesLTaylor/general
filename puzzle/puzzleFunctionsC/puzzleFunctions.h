#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <string.h>
#include <math.h>

#ifndef UTILFUNCTIONS_H 
    
#define UTILFUNCTIONS_H

#ifndef max
    #define max( a, b ) ( ((a) > (b)) ? (a) : (b) )
#endif

#ifndef min
    #define min( a, b ) ( ((a) < (b)) ? (a) : (b) )
#endif

#define oneTOtwo(i,j, nCol) ((i)*nCol + (j))

int TemplateMatch_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result);
int TemplateMatch_V_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result);
int TemplateMatch_C_fast(int* img, int rowsImg, int colsImg, int* templateImg, int* mask, int rowsTpl, int colsTpl, int* result);

#endif  //UTILFUNCTIONS_H