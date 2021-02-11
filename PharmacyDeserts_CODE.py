# import arcpy and set workspace
import arcpy
from arcpy.sa import *
arcpy.env.overwriteOutput = True
arcpy.env.workspace = "H:\GEOG 6308\PharmacyDeserts"
arcpy.CheckOutExtension("Spatial")

# set parameters for: all layers?, output path
arcpy.GetParameterAsText(0)

# get the map document
mxd = arcpy.mapping.MapDocument(r"H:\GEOG 6308\PharmacyDeserts\Untitled.mxd")

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layers
censustracts = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\Census_Tracts_in_2010-shp\Census_Tracts_in_2010.shp")
medianincome = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\ACS_2018_Median_Household_Income_Variables_Tract-shp\ACS_2018_Median_Household_Income_Variables_Tract.shp")
streetsegments = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\Street_Segments_(Retired)-shp\Street_Segments_(Retired).shp")
pharmlocations = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\Pharmacy_Locations-shp\Pharmacy_Locations.shp")

# add the layer to the map at the bottom of the TOC in data frame 0
arcpy.mapping.AddLayer(df, pharmlocations,"BOTTOM")
arcpy.mapping.AddLayer(df, streetsegments,"BOTTOM")
arcpy.mapping.AddLayer(df, medianincome,"BOTTOM")
arcpy.mapping.AddLayer(df, censustracts,"BOTTOM")

#save a copy to the mxd
mxd.saveACopy("H:\GEOG 6308\PharmacyDeserts\DC_PharmacyDeserts.mxd")

# Open KDE
# outKDens = KernelDensity(in_features, population_field, {cell_size}, {search_radius}, {area_unit_scale_factor}, {out_cell_values}, {method})
# Set local variables
in_features = pharmlocations
population_field = "NONE"

# run KDE
outKDens = arcpy.sa.KernelDensity(in_features, population_field)

#save output
outKDens.save("H:\GEOG 6308\PharmacyDeserts\pharm_kernel.tif")

# open raster calculator and set all 0s in outKDens to null
fixedKDens = SetNull(outKDens == 0, outKDens)
outKDens.save()


#run zonal stats comparing the location of pharmacy raster with census tracts
in_zone_data = censustracts
zone_field = "P0010001" # this is the total population in each census tract
in_value_raster = fixedKDens
statistics_type = "MEAN"
cens_pharms = arcpy.sa.ZonalStatistics(in_zone_data, zone_field, in_value_raster, statistics_type)
cens_pharms.save("H:\GEOG 6308\PharmacyDeserts\zstat_census_pharms.tif")

#run zonal stats comparing the location of pharmacy raster with median income inflation adjusted
in_zone = medianincome
zfield = "B19049_001"
in_raster = fixedKDens
stats_type = "MEAN"
medinc_pharms = arcpy.sa.ZonalStatistics(in_zone, zfield, in_raster, stats_type)
medinc_pharms.save("H:\GEOG 6308\PharmacyDeserts\zstat_medinc_pharms.tif")

# create the outputs as raster layers
pharms_ras = arcpy.MakeRasterLayer_management("H:\GEOG 6308\PharmacyDeserts\pharm_kernel.tif", "pharms")
censpharms_ras = arcpy.MakeRasterLayer_management("H:\GEOG 6308\PharmacyDeserts\zstat_census_pharms.tif", "census_pharms")
medincpharms_ras = arcpy.MakeRasterLayer_management("H:\GEOG 6308\PharmacyDeserts\zstat_medinc_pharms.tif", "medinc_pharms")
# create layers 
pharms = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\pharm_kernel.tif")
censpharms = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\zstat_census_pharms.tif")
medincpharms = arcpy.mapping.Layer("H:\GEOG 6308\PharmacyDeserts\zstat_medinc_pharms.tif")
# add the layers to the map document
arcpy.mapping.AddLayer(df, pharms, "TOP")
arcpy.mapping.AddLayer(df, censpharms, "TOP")
arcpy.mapping.AddLayer(df, medincpharms, "TOP")

# save the additions
mxd.save()

