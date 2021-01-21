import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import math
import json

import arcpy
from arcpy.sa import Con
from arcpy.sa import Raster
from arcpy.sa import FocalStatistics
from arcpy.sa import ZonalStatisticsAsTable
from arcpy.sa import IsNull
from arcpy.sa import NbrCircle
from arcpy.sa import Log10
from arcpy import env
from arcpy.sa import *
import os
import sys, locale

relpath = os.path.dirname(sys.argv[0])

arcpy.env.workspace = r"F:\Documents\Hydrologic_Package_2020-12-09\Afstroomanalyse"
work_location = r"F:\Documents\Hydrologic_Package_2020-12-09"
save_location = r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\data"
# save_location = r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\data\generated\combined_affected_houses.csv"


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
x = 'Ondiep'

DREMPEL = 0.02 #m
YEARS = 20.0
SAG = 0.1 #cm/year
RAINHEIGHTS = [32,40,47,58]
CHANCES = {25:40.0, 32:10.0, 40:25.0, 47:50.0, 58:100.0} #mm rain to once in x years

combined = pd.DataFrame(columns = ['FID','MAX'])
for rainHeight in RAINHEIGHTS:
    try:
        houses = pd.read_csv(save_location+r'\waterInHuizen_{}.csv'.format(rainHeight), usecols=['FID','MAX'])
        houses = houses[houses["MAX"] > DREMPEL]
        houses['CHANCE'] = YEARS / CHANCES[rainHeight]
        combined = pd.concat([combined,houses])
    except IOError:
        print('File waterInHuizen_{}.csv not found'.format(rainHeight))

combined = combined.drop_duplicates(subset=['FID'], keep='first')
combined.to_csv(save_location+r"\generated\combined_affected_houses.csv", index = False, header=True)

affectedHouses = arcpy.MakeTableView_management(in_table=save_location+r"\generated\combined_affected_houses.csv", out_view='affectedHousesTemp')

mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

path = work_location+r"\Afstroomanalyse\Buurten\{}\tijdelijk\pandPolygon_clip.shp".format(x)
print(path)
shapeFile = arcpy.mapping.Layer(path)
arcpy.mapping.AddLayer(df, shapeFile,"BOTTOM")
# pandPoly = arcpy.MakeTableView_management(in_table=work_location+r"\Afstroomanalyse\Buurten\{}\tijdelijk\pandPolygon_clip.shp".format(x), out_view='pandPolygon_clip')
joined = arcpy.AddJoin_management("pandPolygon_clip", "FID", affectedHouses, "FID")
lyr = arcpy.mapping.ListLayers(mxd, "pandPolygon_clip", df)[0]
source = arcpy.mapping.Layer(r"F:\Documents\Hydrologic_Package_2020-12-09\symbolTest.lyr")
arcpy.mapping.UpdateLayer(df, lyr, source)

df.extent = lyr.getExtent()
arcpy.mapping.ExportToPNG(mxd, r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\data\generated\ProjectDataFrame.png", df,
    df_export_width=1920,
    df_export_height=1080,
    resolution=360)
# execfile(r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\draw_intersection.py")