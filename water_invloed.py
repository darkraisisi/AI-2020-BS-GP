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

arcpy.env.workspace = r"F:\Documents\Hydrologic_Package_2020-12-09\Afstroomanalyse"
work_location = r"F:\Documents\Hydrologic_Package_2020-12-09\Afstroomanalyse"
save_location = r"C:\Users\david\Documenten\Jaar 2\B\BS\AI-2020-BS-GP\data"

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')
x = 'Ondiep'

# Na bui intersect met panden table generator
# Process: Select all buildings which overlap with their buffer and the highest level of Water on the streets
outZonalStatstable = ZonalStatisticsAsTable(os.path.join(work_location, r"Buurten\{}\tijdelijk\pandPolygon_Buffer.shp").format(x), "FID", os.path.join(work_location, r"Buurten\{}\resultaten\WS_na_bui.tif").format(x),"WaterInHouses","DATA","MAXIMUM")


arcpy.TableToTable_conversion(outZonalStatstable, save_location, "waterInHuizen_Test.csv", '')