/*******************************************************************************
 * Macro Name: Octagon
 * Creator  : Guilhem Ribeill
 *
 * Makes an octagon in the current cell
 *
 * Revision History:
 * 27 Mar 2010	Generated by L-Edit
 *******************************************************************************/
#define PI 3.14159265359

module Octagon
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

	void Octagon(void)
	{	
		
      LCell	pCell	=	LCell_GetVisible();
		LFile	pFile	=	LCell_GetFile(pCell);		
		LLayer pLayer; 
		
		LCoord X, Y;
		LPoint ptArray[12];
		
		int idx = 0;
		double theta;
		double xx, yy;
		double area;
		
        LDialogItem Dialog_Items[4] = {{"Layer", "FUCK"}, {"X Center (micron)", "0"}, {"Y Center (micron)", "0"}, {"Area (micron^2)", "2"} };		
        LCoord Xc, Yc, Rad ;    //Xc = Dodecahedron XCenter, Yc = Dodecahedron YCenter , Area = area of Dodecahedron
        
		
        if ( LDialog_MultiLineInputBox ( "Octagon  Parameters", Dialog_Items, 4 ) )
        {
            pLayer = LLayer_Find(pFile, Dialog_Items[0].value);
            Xc = atol(Dialog_Items[1].value)*1000;
            Yc = atol(Dialog_Items[2].value)*1000;
            area = atol(Dialog_Items[3].value);
          
          
        }

		Rad = sqrt(area/(sqrt(2.)*2.))*1000;

		//Rad = 0.84*1000;
		//LPoint center;
		//center = LPoint_Set(5000,5000);
      //LCoord radius;
      //radius = 5000;
		for (idx=0; idx < 8; idx++)
		{
			theta = idx*(2*PI/8.) - 2.*PI/16.;
			
			xx = Xc + Rad*cos(theta);
			yy = Yc + Rad*sin(theta);
			
			//X = LFile_DispUtoIntU(pFile, xx);
			//Y = LFile_DispUtoIntU(pFile, yy);
			
			ptArray[idx].x = xx;
			ptArray[idx].y = yy; 
		
		}
		
		LPolygon_New(pCell, pLayer, ptArray,8);
      //LCircle_New(pCell, pLayer, center, radius);
	}	
	void Octagon_register(void)
	{
		LMacro_BindToMenuAndHotKey_v9_30("Tools", NULL /*hotkey*/, "Octagon", "Octagon",  NULL /*hotkey category*/);
	}

}
Octagon_register();