/*******************************************************************************
 * Macro Name: CurveWire
 * Creator  : Guilhem Ribeill
 * 
 * Makes a curved (section of a circle) wire in the current cell
 *
 * Revision History:
 * 6 Jul 2011	Generated by L-Edit
 *******************************************************************************/
#define PI 3.141592653589796

module Curve_macro_module
{
#include <stdlib.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <malloc.h>
#include "ldata.h"
/* Begin -- Remove this block if you are not using L-Comp. */
#include "lcomp.h"
/* End */

	void Curve(void)
	{
		LCell	pCell	=	LCell_GetVisible();
		LFile	pFile	=	LCell_GetFile(pCell);
		
		int idx;
		
		float dtheta, theta0, theta1;
		
		float r1;			//inner radius
		float r2;			//outer radius
		float rad;			//center radius
		float Xc, Yc;		//center coordinates
		float width;		//wire width
		int nSegments;		//number of segments
		
		LLayer pLayer;    //layer to draw on
		
		LPoint *ptArray; //points for polygon
		
		float xt, yt;
		
		LDialogItem Dialog_Items[8] = {{"Number of Segments", "8"}, {"Wire Width", "6"}, {"Inner Radius", "10"}, {"X", "0"}, {"Y", "0"}, {"Start Angle (deg.)", "-90"}, {"End Angle (deg.)", "0"}, {"Layer", "Base" }};
	
		if ( LDialog_MultiLineInputBox ( "Curve Parameters", Dialog_Items, 8 ) )
      {
          nSegments = atoi(Dialog_Items[0].value);
          width = atof(Dialog_Items[1].value);
          rad = atof(Dialog_Items[2].value);
          Xc = atof(Dialog_Items[3].value);
          Yc = atof(Dialog_Items[4].value);
          theta0 = atof(Dialog_Items[5].value);
          theta1 = atof(Dialog_Items[6].value);
          pLayer = LLayer_Find (pFile, Dialog_Items[7].value);
      }  
      else
      {
      	return;
      }
      
      ptArray = (LPoint*)calloc(2*nSegments+2, sizeof(LPoint));
      
      r1 = rad - width/2.;
      r2 = rad + width/2.;
      
     
      theta0 = PI*theta0/180.;
      theta1 = PI*theta1/180.;
      dtheta = (theta1 - theta0)/(float)nSegments;
		
      
      //top curve
      for (idx = 0; idx < (nSegments+1); idx++)
      {
      	xt = Xc + r1*cos(theta0 + (idx)*dtheta);
      	yt = Yc + r1*sin(theta0 + (idx)*dtheta);
      	
      	ptArray[idx].x = LFile_DispUtoIntU(pFile, xt);
      	ptArray[idx].y = LFile_DispUtoIntU(pFile, yt);
      	
      }
      
      int n=2*nSegments+1;
      
      for (idx = n; idx > (nSegments); idx--)
      {
      	xt = Xc + r2*cos(theta0 + (n-idx)*dtheta);
      	yt = Yc + r2*sin(theta0 + (n-idx)*dtheta);
      	
      	ptArray[idx].x = LFile_DispUtoIntU(pFile, xt);
      	ptArray[idx].y = LFile_DispUtoIntU(pFile, yt);
      	
      }
      
      LPolygon_New(pCell, pLayer,ptArray,2*nSegments+2);
      
      free(ptArray);
		

	}

	void Curve_register(void)
	{
		LMacro_BindToMenuAndHotKey_v9_30("Tools", NULL /*hotkey*/, "DrawCurve", "Curve", NULL /*hotkey category*/);
	}

}
Curve_register();