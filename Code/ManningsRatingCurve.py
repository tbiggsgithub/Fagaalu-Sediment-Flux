# -*- coding: utf-8 -*-
"""
Created on Sat Oct 25 15:39:23 2014

@author: Alex
"""

#### Import modules
## Data Processing
import numpy as np
import pandas as pd
import math
import datetime as dt
import pytz
import matplotlib.pyplot as plt
## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.max_rows', 15)

#### DIRECTORIES
git=True
if git==True: ## Git repository
    maindir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sediment-Flux/' 
    datadir=maindir+'Data/'
    dataoutputdir = datadir+'Output/'
    GISdir = maindir+'Data/GIS/'
    figdir = maindir+'Figures/'
    dirs={'main':maindir,'data':datadir,'GIS':GISdir,'fig':figdir}
elif git!=True: ## Local folders
    maindir = 'C:/Users/Alex/Desktop/'### samoa/
    csvoutputdir = datadir+'samoa/WATERSHED_ANALYSIS/FAGAALU/MasterDataFiles/csv_output/'
    savedir = datadir+'samoa/WATERSHED_ANALYSIS/GoodFigures/'
    figdir = datadir+'samoa/WATERSHED_ANALYSIS/GoodFigures/rawfigoutput/'
    
def Mannings(XSfile,sheetname,Slope,Manning_n,stage_start,stage_end=None,display=True):    
    ## Open and parse file; drop NA  
    print XSfile+' '+sheetname
    print 'Slope: '+str(Slope)+' Mannings n: '+str(Manning_n)
    XL = pd.ExcelFile(XSfile) 
    df = XL.parse(sheetname,header=4,parse_cols='F:H')
    df = df.dropna()
    ## Mannings Parameters S:slope, n:Mannings n
    S = Slope # m/m
    n= Manning_n
    ## empty lists
    areas, wp, v, q, = [],[],[],[]
    ## Stage data
    ## one stage measurement
    if stage_end == None:
        print 'Stage: '+str(stage_start)
        stages = np.array([stage_start])
    ## start and end stage
    elif stage_start != stage_end:
        print 'Stage_start: '+str(stage_start)+' Stage_end: '+str(stage_end)
        stages = np.arange(stage_start,stage_end,.1) #m
    ## stage Series         
    elif type(stage_start)==pd.Series:
        print 'Stage Series...'
        stages = stage_start.to_list()
        
    for stage in stages:
        print 'stage: '+str(stage)
        df['y1'] = df['depth']+df['Rod Reading'].max()
        df['y2'] = stage
        df['z'] = df['y2']-df['y1']
        df['z'] = df['z'][df['z']>=0]
        
        x = df['Dist'].values
        y1 = df['y1'].values
        y2 = df['y2'].values
        
        z = y2-y1
        z= np.where(z>=0,z,0)
        Area = np.trapz(z,x)
        
        ## Wetted Perimeter0.01
        df['dx'] =df['Dist'].sub(df['Dist'].shift(1),fill_value=0)
        df['dy'] = df['z'].sub(df['z'].shift(1),fill_value=0)
        df['wp'] = (df['dx']**2 + df['dy']**2)**0.5
        WP = df['wp'].sum()
        R = (Area/WP) ## m2/m = m
        ## Mannings = (1R^2/3 * S^1/2)/n
        ManningV = (1*(R**(2.0/3.0))*(S**0.5))/n
        ManningQ = ManningV * Area ## M3/s
        
        if display == True:
            fig, ax1 = plt.subplots(1)
            ax1.plot(df['Dist'],df['y1'],'-o',c='k')
            ax1.fill_between(df['Dist'], df['y1'], stage,where = df['y1']<=stage,alpha=.5, interpolate=True)
            ax1.annotate('stage: '+'%.2f'%stage+'m',xy=(df['Dist'].min(),stage+.45))
            ax1.annotate('Mannings n: '+str(n),xy=(df['Dist'].min(),stage+.03))
            ax1.annotate('Area: '+'%.3f'%Area+'m2',xy=(df['Dist'].min(),stage+.25))
            ax1.annotate('WP: '+'%.2f'%WP+'m',xy=(df['Dist'].mean(),stage+.03))
            ax1.annotate('Manning V: '+'%.2f'%ManningV+'m/s ',xy=(df['Dist'].mean(),stage+.25))
            ax1.annotate('Manning Q: '+'%.3f'%ManningQ+'m3/s',xy=(df['Dist'].mean(),stage+.45))
            plt.axes().set_aspect('equal')
            plt.xlim(-1,df['Dist'].max()+1),plt.ylim(-1,stage + 1.)
    
        areas.append(Area)
        wp.append(WP)
        v.append(ManningV)
        q.append(ManningQ)
        
    DF = pd.DataFrame({'stage':stages,'area':areas,'wp':wp,'vel':v,'Q':q})
    return DF
#XSfile, sheetname, Slope, Manning_n =   datadir+'Q/LBJ_cross_section.xlsx', 'LBJ_m', .01, .05
#max_LBJ = Fagaalu_stage_data['LBJ'].max()/100 #cm to m
Man_stages = Mannings(datadir+'Q/LBJ_cross_section.xlsx','DAM_m',Slope=0.044,Manning_n=0.05,stage_start=1.20)

def Mannings_Series(XSfile,sheetname,Slope,Manning_n,stage_series):    
    ## Open and parse file; drop NA  
    print XSfile+' '+sheetname
    print 'Slope: '+str(Slope)+' Mannings n: '+str(Manning_n)
    XL = pd.ExcelFile(XSfile) 
    df = XL.parse(sheetname,header=4,parse_cols='F:H')
    df = df.dropna()
    ## Mannings Parameters S:slope, n:Mannings n
    S = Slope # m/m
    n= Manning_n
    ## empty lists
    areas, wp, v, q, = [],[],[],[]
    ## Stage data
    stage_series = stage_series/100 ## cm to m
    stages = stage_series.values
        
    for stage in stages:
        #print 'stage: '+str(stage)
        df['y1'] = df['depth']+df['Rod Reading'].max()
        df['y2'] = stage
        df['z'] = df['y2']-df['y1']
        df['z'] = df['z'][df['z']>=0]
        
        x = df['Dist'].values
        y1 = df['y1'].values
        y2 = df['y2'].values
        
        z = y2-y1
        z= np.where(z>=0,z,0)
        Area = np.trapz(z,x)
        
        ## Wetted Perimeter0.01
        df['dx'] =df['Dist'].sub(df['Dist'].shift(1),fill_value=0)
        df['dy'] = df['z'].sub(df['z'].shift(1),fill_value=0)
        df['wp'] = (df['dx']**2 + df['dy']**2)**0.5
        WP = df['wp'].sum()
        R = (Area/WP) ## m2/m = m
        ## Mannings = (1R^2/3 * S^1/2)/n
        ManningV = (1*(R**(2.0/3.0))*(S**0.5))/n
        ManningQ = ManningV * Area ## M3/s
    
        areas.append(Area)
        wp.append(WP)
        v.append(ManningV)
        q.append(ManningQ)
        
    DF = pd.DataFrame({'stage':stages,'area':areas,'wp':wp,'vel':v,'Q':q},index=stage_series.index)
    return DF
#Man = Mannings_Series(datadir+'Q/LBJ_cross_section.xlsx','LBJ_m',Slope=0.016,Manning_n=0.05,stage_series=Fagaalu_stage_data['LBJ'])