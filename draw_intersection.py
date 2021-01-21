import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import math
import json
from colour import Color as clr
from PIL import Image, ImageDraw, ImageFont

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


arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
x = 'Ondiep'

DREMPEL = 0.02 #m
YEARS = 20
SAG = 0.1 #cm/year
RAINHEIGHTS = [32,40,47,58]
CHANCES = {25:15, 32:87.8, 40:55.8, 47:33.2, 58:18.2} #mm rain to once in x years

combined = pd.DataFrame(columns = ['FID','MAX'])
for rainHeight in RAINHEIGHTS:
    try:
        houses = pd.read_csv(save_location+r'\waterInHuizen_{}.csv'.format(rainHeight), usecols=['FID','MAX'])
        houses = houses[houses["MAX"] > DREMPEL]
        houses['CHANCE'] = CHANCES[rainHeight]
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
joined = arcpy.AddJoin_management("pandPolygon_clip", "FID", affectedHouses, "FID")
lyr = arcpy.mapping.ListLayers(mxd, "pandPolygon_clip", df)[0]
source = arcpy.mapping.Layer(save_location+r"\symbology.lyr")
arcpy.mapping.UpdateLayer(df, lyr, source)

df.extent = lyr.getExtent()
arcpy.mapping.ExportToPNG(mxd, r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\data\generated\ProjectDataFrame.png", df,
    df_export_width=1920,
    df_export_height=1080,
    resolution=960)

n = combined['CHANCE'].nunique()
unique = combined['CHANCE'].unique()
colors = list(clr('red').range_to(clr("yellow"),n))

image = Image.open(save_location+r"\generated\ProjectDataFrame.png")
width, height = image.size
width, height

draw = ImageDraw.Draw(image)
text = 'Kans in 20 jaar'
fontSize = 28
margin = fontSize /5
leftMargin = 5
font = ImageFont.truetype("arial.ttf", fontSize)
textwidth, textheight = draw.textsize(text,font=font)

textwidth, textheight, text, tuple([int(255*x) for x in colors[1].rgb])
draw.multiline_text((leftMargin+0, 0), text, (0,0,0), font=font)

for i in range(n+1):
    blockHeight = (textheight + margin) * (i+1)
    blockWidth = 20
    if i != n:
        draw.multiline_text((blockWidth + 10, blockHeight), "{}%".format(unique[i]), (0,0,0), font=font)
        draw.rectangle([leftMargin+0, blockHeight+5, leftMargin+blockWidth, blockHeight+25],outline=(0,0,0),fill=tuple([int(255*x) for x in colors[i].rgb]))
    else:
        draw.multiline_text((blockWidth + 10, blockHeight), "Ongehinderd", (0,0,0), font=font)
        draw.rectangle([leftMargin+0, blockHeight+5, leftMargin+blockWidth, blockHeight+25],outline=(0,0,0),fill=tuple([int(255*x) for x in clr('green').rgb]))
        
image.save(save_location+r"\generated\ProjectDataFrame.png")
# execfile(r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\draw_intersection.py")