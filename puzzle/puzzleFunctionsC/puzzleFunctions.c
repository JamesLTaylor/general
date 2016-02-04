#include "puzzleFunctions.h"
#include <stdio.h>

int TemplateMatch_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result)
{    
    int row, col, index1, index2, index3, i, j;
    int nRows = (rowsImg - rowsTpl);
    int nCols = (colsImg - colsTpl);
    double temp;
    double diff;

    //printf("rowsImg = %i \n", rowsImg);
    //printf("colsImg = %i \n", colsImg);
    //printf("rowsTpl = %i \n", rowsTpl);
    //printf("colsTpl = %i \n", colsTpl);
    //printf("nRows = %i \n", nRows);
    //printf("nCols = %i \n", nCols);
    //printf("started\n");
    
    for (row=0; row<nRows; row++)
    //for (row=0; row<1; row++)
    {
        for (col=0; col<nCols; col++)
        //for (col=0; col<1; col++)
        {
            temp = 0.0;
            for (i=0; i<rowsTpl; i++){
                for (j=0; j<colsTpl; j++){
                    index1 = (i*colsTpl) + j;
                    if (mask[index1]>0){
                        index2 = (row+i)*colsImg + (col+j);                 
                        diff = img[index2] - templateImg[index1];
                        temp += ((diff<0)?(-diff):diff);
                        //printf("%i, %i, %f, %f, %f, %f \n", i, j, img[index2], templateImg[index1], abs(img[index2] - templateImg[index1]), temp);
                    }
                }
            }
            index3 = row * nCols + col;
            //printf("temp = %f", temp);
            result[index3] = temp;
        }
        //printf("row = %i ", row);
        //printf("col = %i \n", col);
    }

    //result[5] = 20.0;     
    return 0;
}


/*
Checks whether the top left corner of the piece is close to an expected 
*/
int inRange(int x, int y, , double offsetX, double offsetY, 
			double pieceRows, double pieceCols, int rangeSize)
{
    double nPieces, fracPieces;
    
	temp = x/pieceCols;
	fracPieces = temp - floor(temp);
	if ((fracPieces*pieceCols)<rangeSize) return 1;
	
	temp = y/pieceRows;
	fracPieces = temp - floor(temp);
	if ((fracPieces*pieceRows)<rangeSize) return 1;
	
	return 0;
	
	
	
	
}


int TemplateMatch_V_C(double* img, int rowsImg, int colsImg, double* templateImg, double* mask, int rowsTpl, int colsTpl, double* result)
{    
    int row, col, index1, index2, index3, i, j;
    int nRows = (rowsImg - rowsTpl);
    int nCols = (colsImg - colsTpl);
    double temp;
    double diff;
    double templateMeanBrightness = 0;
    double patchMeanBrightness = 0;
    int pixelCount = 0;
    double compare;

    printf("brightness adjusted matching\n");
    // Get the template mean brightness
    for (i=0; i<rowsTpl; i++){
        for (j=0; j<colsTpl; j++){
            index1 = (i*colsTpl) + j;
            if (mask[index1]>0){
                pixelCount++;
                templateMeanBrightness += templateImg[index1];
            }
        }
    }
    templateMeanBrightness = templateMeanBrightness / pixelCount;
   
    for (row=0; row<nRows; row++)    
    {
        for (col=0; col<nCols; col++)        
        {            
            // First get the mean brightness of the comparison patch in the image
            patchMeanBrightness = 0;
            pixelCount = 0;
            for (i=0; i<rowsTpl; i++){
                for (j=0; j<colsTpl; j++){
                    index1 = (i*colsTpl) + j;
                    if (mask[index1]>0){                        
                        pixelCount++;
                        index2 = (row+i)*colsImg + (col+j);
                        patchMeanBrightness += img[index2];
                    }
                }
            }
            patchMeanBrightness = patchMeanBrightness/pixelCount;

            temp = 0.0;
            for (i=0; i<rowsTpl; i++){
                for (j=0; j<colsTpl; j++){
                    index1 = (i*colsTpl) + j;
                    if (mask[index1]>0){
                        index2 = (row+i)*colsImg + (col+j);
                        compare = img[index2] * templateMeanBrightness/patchMeanBrightness;
                        compare = (compare>255)?255:compare;
                        diff = compare - templateImg[index1];
                        temp += ((diff<0)?(-diff):diff);
                        //printf("%i, %i, %f, %f, %f, %f \n", i, j, img[index2], templateImg[index1], abs(img[index2] - templateImg[index1]), temp);
                    }
                }
            }
            index3 = row * nCols + col;
            //printf("temp = %f", temp);
            result[index3] = temp;
        }
        //printf("row = %i ", row);
        //printf("col = %i \n", col);
    }

    //result[5] = 20.0;     
    return 0;
}


int TemplateMatch_C_fast(int* img, int rowsImg, int colsImg, int* templateImg, int* mask, int rowsTpl, int colsTpl, int* result)
{    
    int row, col, index1, index2, index3, i, j;
    int nRows = (rowsImg - rowsTpl);
    int nCols = (colsImg - colsTpl);
    int temp;
    int diff;
    
    index3 = 0;
    for (row=0; row<nRows; row++)
    {
        for (col=0; col<nCols; col++)
        {
            temp = 0;
            index1 = 0;
            for (i=0; i<rowsTpl; i++){
                for (j=0; j<colsTpl; j++){
                    //index1 = (i*colsTpl) + j;                    
                    if (mask[index1]>0){
                        index2 = (row+i)*colsImg + (col+j);                 
                        diff = img[index2] - templateImg[index1];
                        temp += ((diff<0)?(-diff):diff);
                    }
                    index1++;
                }
            }
            //index3 = row * nCols + col;            
            result[index3] = temp;
            index3++;
        }
    }
    return 0;
}