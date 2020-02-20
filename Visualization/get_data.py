# import geopandas as gpd
# import matplotlib.pyplot as plt
# import matplotlib
# import pandas as pd
# from pandas import Series
# import numpy as np
# import os
# import json
# import random
# from shapely import geometry
# from shapely.geometry.polygon import Polygon
# from shapely.geometry.multipolygon import MultiPolygon

# def explode(indata):
#     indf = gpd.GeoDataFrame.from_file(indata)
#     outdf = gpd.GeoDataFrame(columns=indf.columns)
#     for idx, row in indf.iterrows():
#         if type(row.geometry) == Polygon:
#             outdf = outdf.append(row,ignore_index=True)
#         if type(row.geometry) == MultiPolygon:
#             multdf = gpd.GeoDataFrame(columns=indf.columns)
#             recs = len(row.geometry)
#             multdf = multdf.append([row]*recs,ignore_index=True)
#             for geom in range(recs):
#                 multdf.loc[geom,'geometry'] = row.geometry[geom]
#             outdf = outdf.append(multdf,ignore_index=True)
#     return outdf

# def filter_columns(df, keep):
#     """Filter Pandas table df keeping only columns in keep"""
#     cols = list(df)
#     for col in keep:
#         cols.remove(col)

#     return df.drop(columns=cols)

# def income_binning(return_colors=False):
#     """Return bins and color scheme for relative median income"""
#     # First bin is -10 000..-8 000, next is -8 000..-6 000, ..., final is 14 000-16 000
#     bins = np.arange(-10000,18000,2000)
#     cmap = plt.cm.get_cmap('RdBu', len(bins))
#     if not return_colors:
#         return bins, cmap
#     else:
#         colors = []
#         for i in range(cmap.N):
#             rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
#             colors.append(matplotlib.colors.rgb2hex(rgb))

#         return bins, colors

# def pop_density_binning(return_colors=False):
#     """Return bins and color scheme for population density"""
#     # First bin is 0, next is 0.1-1, ..., final is > 10000
#     bins = np.array([0, 1, 2, 4, 6, 8, 10, 50, 100, 200, 500, 1000, 1500, 2000, 2500, 5000, 10000])
#     cmap = plt.cm.get_cmap('Reds', len(bins)+1)
#     if not return_colors:
#         return bins, cmap
#     else:
#         colors = []
#         for i in range(cmap.N):
#             rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
#             colors.append(matplotlib.colors.rgb2hex(rgb))

#         return bins, colors

# def pop_binning(return_colors=False):
#     bins = np.array([x for x in range(0,30000,3000)])
#     cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
#     if not return_colors:
#         return bins, cmap
#     else:
#         colors = []
#         for i in range(cmap.N):
#             rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
#             colors.append(matplotlib.colors.rgb2hex(rgb))

#         return bins, colors

# def trip_binning(return_colors=False):
#     bins = np.array([x for x in range(0,100000,10000)])
#     cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
#     if not return_colors:
#         return bins, cmap
#     else:
#         colors = []
#         for i in range(cmap.N):
#             rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
#             colors.append(matplotlib.colors.rgb2hex(rgb))

#         return bins, colors

# def main():
#     """
#     # Get statistics from Statistics Finland portal for year 2018 keeping only the selected data columns
#     url = "http://geo.stat.fi/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=postialue:pno_tilasto_2018&outputFormat=json"
#     keep_columns = ['nimi', 'posti_alue', 'he_vakiy', 'geometry', 'pinta_ala', 'hr_mtu']
#     data = filter_columns(gpd.read_file(url), keep_columns)

#     # Rename columns
#     data.rename(columns={'he_vakiy': 'pop2018', 'pinta_ala': 'area', 'nimi': 'name', 'hr_mtu': 'income', 'posti_alue': 'zip'}, inplace=True)

#     # Convert geometry to Google Maps compatible Lat/Long coordinates
#     data.to_crs({'init': 'epsg:4326'}, inplace=True)

#     # Income data in some postal code areas might be undefined (NaNs or -1.0)
#     # In these areas, there are either no inhabitants at all, or too few inhabitans
#     # so the income data is not shown for privacy reasons
#     # Set the income in these regions to the national average
#     data.replace(-1.0, np.nan, inplace=True)
#     avg_income = np.nanmean(data['income'])
#     data.fillna(avg_income, inplace=True)

#     # Add column relative median income (w.r.t national average)
#     data['income_relative'] = data['income']-avg_income

#     # Add column for population density
#     # First convert area from m^2 to km^2
#     data['area'] *= 1e-6
#     # Now calculate density in in citizens/km^2
#     data['pop_density'] = data['pop2018']/data['area']

#     # Round data to 2 decimal places to reduce size of resulting GeoJSON file
#     data = data.round({'pop_density': 2, 'income_relative': 2})
#     # To further reduce the file size, we could round the coordinates
#     # of the Polygon objects as well
#     # This is quite cumbersome with GeoPandas, so I opted to use the ogr2ogr tool

#     # Assign colors to zip codes based on relative median income by binning data
#     bins, cmap = income_binning()
#     colors = []

#     for i, row in data.iterrows():
#         index = bins.searchsorted(row['income_relative'])
#         colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

#     data['fill'] = Series(colors, dtype='str', index=data.index)

#     # Assign alternative colors for population density
#     bins, cmap = pop_density_binning()
#     colors = []

#     for i, row in data.iterrows():
#         index = bins.searchsorted(row['pop_density'])
#         colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

#     data['fill_density'] = Series(colors, dtype='str', index=data.index)

#     # Save data as GeoJSON
#     # Note the driver cannot overwrite an existing file,
#     # so we must remove it first
#     outfile = 'map_data.json'
#     if os.path.isfile(outfile):
#         os.remove(outfile)

#     data.to_file(outfile, driver='GeoJSON')
#     """

#     json_file = 'ca_california_zip_codes_geo.min.json'
#     data = gpd.read_file(json_file)

#     # Rename columns
#     data.rename(columns={'ZCTA5CE10': 'zipcode'}, inplace=True)
#     data = data[['zipcode', 'geometry']]

#     # data.to_crs({'init': 'epsg:4326'}, inplace=True)

#     N_zipcodes = len(data)

#     geocod_data = pd.read_csv('../../TAMIDS/data/Geocoded_Trip_Data.csv')

#     population, out_trips = [], []
#     for i in range(N_zipcodes):
#         geocod_zipcode = float(data.loc[i]['zipcode'])
#         df = geocod_data[geocod_data['zip'] == geocod_zipcode]
#         pop = sum(np.unique(df['total_population']))
#         trips = len(df)
#         population.append(pop)
#         out_trips.append(trips)

#     data['population'] = population
#     data['trips'] = out_trips
    
#     # Assign colors to zip codes based on population
#     bins, cmap = pop_binning()
#     colors = []

#     for i, row in data.iterrows():
#         index = bins.searchsorted(row['population'])
#         colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

#     data['fill_pop'] = Series(colors, dtype='str', index=data.index)

#     bins, cmap = trip_binning()
#     colors = []

#     # Assign colors to zip codes based on the number of trips
#     for i, row in data.iterrows():
#         index = bins.searchsorted(row['trips'])
#         colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

#     data['fill_trip'] = Series(colors, dtype='str', index=data.index)

#     data = data.explode()

#     outfile = 'map_data.json'
#     if os.path.isfile(outfile):
#         os.remove(outfile)

#     # upcast_dispatch = {geometry.Point: geometry.MultiPoint, 
#     #                    geometry.LineString: geometry.MultiLineString, 
#     #                    geometry.Polygon: geometry.MultiPolygon}

#     # def cast_to_multigeometry(geom):
#     #     caster = upcast_dispatch.get(type(geom), lambda x: x[0])
#     #     return caster([geom])

#     # data.geometry.apply(cast_to_multigeometry)

#     data.to_file(outfile, driver='GeoJSON')
#     print("GeoJSON created!")


# if __name__ == '__main__':
#     main()

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from pandas import Series
import numpy as np
import os
import json
import random
from shapely import geometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


def explode(indata):
    indf = gpd.GeoDataFrame.from_file(indata)
    outdf = gpd.GeoDataFrame(columns=indf.columns)
    for idx, row in indf.iterrows():
        if type(row.geometry) == Polygon:
            outdf = outdf.append(row,ignore_index=True)
        if type(row.geometry) == MultiPolygon:
            multdf = gpd.GeoDataFrame(columns=indf.columns)
            recs = len(row.geometry)
            multdf = multdf.append([row]*recs,ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom,'geometry'] = row.geometry[geom]
            outdf = outdf.append(multdf,ignore_index=True)
    return outdf


def filter_columns(df, keep):
    """Filter Pandas table df keeping only columns in keep"""
    cols = list(df)
    for col in keep:
        cols.remove(col)

    return df.drop(columns=cols)


def income_binning(return_colors=False):
    """Return bins and color scheme for relative median income"""
    # First bin is -10 000..-8 000, next is -8 000..-6 000, ..., final is 14 000-16 000
    bins = np.arange(-10000,18000,2000)
    cmap = plt.cm.get_cmap('RdBu', len(bins))
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def pop_density_binning(return_colors=False):
    """Return bins and color scheme for population density"""
    # First bin is 0, next is 0.1-1, ..., final is > 10000
    bins = np.array([0, 1, 2, 4, 6, 8, 10, 50, 100, 200, 500, 1000, 1500, 2000, 2500, 5000, 10000])
    cmap = plt.cm.get_cmap('Reds', len(bins)+1)
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def pop_binning(return_colors=False):
    bins = np.array([x for x in range(0,20000,3000)])
    cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def trip_binning(return_colors=False):
    bins = np.array([x for x in range(0,100000,10000)])
    cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def age_binning(return_colors=False):
    bins = np.array([x for x in range(0,100,10)])
    cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def household_binning(return_colors=False):
    bins = np.array([x for x in range(0,2000,200)])
    cmap = plt.cm.get_cmap('RdBu', len(bins)+1)
    if not return_colors:
        return bins, cmap
    else:
        colors = []
        for i in range(cmap.N):
            rgb = cmap(i)[:3] # will return rgba, we take only first 3 so we get rgb
            colors.append(matplotlib.colors.rgb2hex(rgb))

        return bins, colors


def main():
    geo_data = gpd.read_file('2010_Census_Block_Groups_Geography_Only/2010_Census_Block_Groups_Geography_Only.shp')

    geo_data.rename(columns={'GEOID10': 'zipcode'}, inplace=True)
    geo_data = geo_data[['zipcode', 'AreaSqMil', 'geometry']]

    data = pd.read_csv('../../TAMIDS/data/Census_Block_Data.csv')
    data.rename(columns={'LABlockShapes.GEOID10': 'zipcode', 'ACS Demographics/Population by age range/Total/Value': 'pop', 'ACS Economics/Median household income/Total/Value': 'tr', 'ACS Demographics/Median age/Total/Value': 'age', 'ACS Economics/Number of households/Total/Value': 'households'}, inplace=True)
    data = data[['zipcode', 'pop', 'tr', 'age', 'households']]

    population, out_trips, age, households = [], [], [], []
    for i, row in data.iterrows():
        population.append(round(row['pop']/geo_data['AreaSqMil'].loc[i], 2))
        out_trips.append(row['tr'])
        age.append(row['age'])
        households.append(row['households'])
    
    geo_data['population'] = population
    geo_data['trips'] = out_trips
    geo_data['age'] = age
    geo_data['households'] = households

     # Assign colors to zip codes based on population
    bins, cmap = pop_binning()
    colors = []

    for i, row in geo_data.iterrows():
        index = bins.searchsorted(row['population'])
        colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

    geo_data['fill_pop'] = Series(colors, dtype='str', index=geo_data.index)

    bins, cmap = trip_binning()
    colors = []

    # Assign colors to zip codes based on the number of trips
    for i, row in geo_data.iterrows():
        index = bins.searchsorted(row['trips'])
        colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

    geo_data['fill_trip'] = Series(colors, dtype='str', index=geo_data.index)

     # Assign colors to zip codes based on population
    bins, cmap = age_binning()
    colors = []

    for i, row in geo_data.iterrows():
        index = bins.searchsorted(row['age'])
        colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

    geo_data['fill_age'] = Series(colors, dtype='str', index=geo_data.index)
    
    # geo_data.to_crs({'init': 'epsg:4326'}, inplace=True)
    # data = flatten_gdf_geometry(data, 'Polygon')
    # geo_data = geo_data.explode()

    # Assign colors to zip codes based on population
    bins, cmap = household_binning()
    colors = []

    for i, row in geo_data.iterrows():
        index = bins.searchsorted(row['households'])
        colors.append(matplotlib.colors.rgb2hex(cmap(index)[:3]))

    geo_data['fill_household'] = Series(colors, dtype='str', index=geo_data.index)
    
    # geo_data.to_crs({'init': 'epsg:4326'}, inplace=True)
    # data = flatten_gdf_geometry(data, 'Polygon')
    geo_data = geo_data.explode()

    outfile = 'map_data.json'
    if os.path.isfile(outfile):
        os.remove(outfile)

    # upcast_dispatch = {geometry.Point: geometry.MultiPoint, 
    #                    geometry.LineString: geometry.MultiLineString, 
    #                    geometry.Polygon: geometry.MultiPolygon}

    # def cast_to_multigeometry(geom):
    #     caster = upcast_dispatch.get(type(geom), lambda x: x[0])
    #     return caster([geom])

    # data.geometry.apply(cast_to_multigeometry)

    geo_data.to_file(outfile, driver='GeoJSON')
    print("GeoJSON created!")


if __name__ == '__main__':
    main()

