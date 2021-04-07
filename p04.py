"""
CS-3435 Project 04: USGS Tiling.

This project was used to connect topographical data from the USGS(United States Geological Survery) into a
complete map showing a 3 degree by 3 degree area.

While it is specific for this project, this could be easily generalized to work with any data from the USGS.

@author Reis Gadsden
@version 4/6/21
"""

# necessary imports
import matplotlib.pyplot as plt
import numpy as np


# builds a file name of given coordinates
def construct_file_name(lat, lon):
    output_lat = ""
    output_lon = ""
    if lat < 0:
        output_lat = "s" + str(abs(lat))
    else:
        output_lat = "n" + str(lat)

    if lon < 0:
        if abs(lon) > 99:
            output_lon = "w" + str(abs(lon))
        else:
            output_lon = "w0" + str(abs(lon))
    else:
        if abs(lon) > 99:
            output_lon = "e" + str(abs(lon))
        else:
            output_lon = "e0" + str(abs(lon))

    file_name = "./ncdata/USGS_NED_1_" + output_lat + output_lon + "_IMG.tif"
    return file_name


# USGS data contains a 6 pixel overlap, this will trim of overlapping data
def load_trim_image(lat, lon):
    im = plt.imread(construct_file_name(lat, lon))
    image = im[6:len(im) - 6, 6:len(im) - 6]
    return image


# will stitch four images together
def stitch_four(lat, lon):
    lat_neg = lat/abs(lat)
    lon_neg = lon/abs(lon)

    imagenw = load_trim_image(lat, lon)
    imagene = load_trim_image(lat, int(abs(lon+1)*lon_neg))
    imagesw = load_trim_image(int(abs(lat-1)*lat_neg), lon)
    imagese = load_trim_image(int(abs(lat-1)*lat_neg), int(abs(lon+1)*lon_neg))

    x = np.concatenate([imagene, imagenw], axis=1)

    y = np.concatenate([imagese, imagesw], axis=1)

    image = np.concatenate([x, y], axis=0)
    return image


# gets a row of latitude with a specified amount of longitude tiles
def get_row(lat, lon_min, num_tiles):
    lat_neg = lat/abs(lat)
    lon_neg = lon_min/abs(lon_min)
    imagefirst = load_trim_image(lat, lon_min)

    images_to_concat = []
    if num_tiles > 1:
        for i in range(1, num_tiles):
            images_to_concat.append(load_trim_image(lat, (int((abs(lon_min) - i) * lon_neg))))

        image = np.concatenate([imagefirst, images_to_concat[0]], axis=1)
        i = 1
        while i < len(images_to_concat):
            image = np.concatenate([image, images_to_concat[i]], axis=1)
            i += 1
    else:
        image = imagefirst

    return image


# builds a tiled area based of the northwest coordinates and given additional lon and lat tiles
def get_tile_grid(lat_max, lon_min, num_lat, num_lon):
    if num_lat > 1:
        rows = []
        for i in range(0, num_lat):
            rows.append(get_row(lat_max-i, lon_min, num_lon))

        image = np.concatenate([rows[0], rows[1]], axis=0)
        i = 2
        while i < len(rows):
            image = np.concatenate([image, rows[i]], axis=0)
            i += 1
    else:
        image = get_row(lat_max, lon_min, num_lon)

    return image


# gets the northwest coordinate of a non-integer coordinate
def get_northwest(lat, lon):
    if lat > 0:
        nw_lat = np.ceil(lat)
    else:
        nw_lat = np.floor(lat)

    if lon > 0:
        nw_lon = np.ceil(lon)
    else:
        nw_lon = np.floor(lon)
    return int(nw_lat), int(nw_lon)


# builds a tiled grid from non-integer coordinates
def get_tile_grid_decimal(northwest, southeast):
    nw_lat, nw_lon = get_northwest(*northwest)
    se_lat, se_lon = get_northwest(*southeast)
    print("nw: " + str(nw_lat) + " " + str(nw_lon))
    print("se: " + str(se_lat) + " " + str(se_lon))
    image = get_tile_grid(lat_max=nw_lat, lon_min=nw_lon, num_lat=abs(nw_lat - se_lat)+1, num_lon=abs(nw_lon - se_lon)+1)
    return image


# a small example
im = get_tile_grid(38, -84, 3, 3)
plt.imshow(im)
plt.colorbar()
plt.show()
