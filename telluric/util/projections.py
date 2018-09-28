"""Projection utilities.

"""
from functools import partial

import pyproj
from shapely import ops

from rasterio.crs import CRS

from telluric.constants import WGS84_CRS


def generate_transform(source_crs, destination_crs):
    original = pyproj.Proj(dict(source_crs), preserve_units=True)
    destination = pyproj.Proj(dict(destination_crs), preserve_units=True)

    transformation = partial(
        pyproj.transform,
        original, destination
    )

    return partial(ops.transform, transformation)


def transform(shape, source_crs, destination_crs=None, src_affine=None, dst_affine=None):
    """Transforms shape from one CRS to another.

    Parameters
    ----------
    shape : shapely.geometry.base.BaseGeometry
        Shape to transform.
    source_crs : dict or str
        Source CRS in the form of key/value pairs or proj4 string.
    destination_crs : dict or str, optional
        Destination CRS, EPSG:4326 if not given.
    src_affine: Affine, optional.
        input shape in relative to this affine
    dst_affine: Affine, optional.
        output shape in relative to this affine

    Returns
    -------
    shapely.geometry.base.BaseGeometry
        Transformed shape.

    """
    if destination_crs is None:
        destination_crs = WGS84_CRS

    if src_affine is not None:
        shape = ops.transform(lambda r, q: ~src_affine * (r, q), shape)

    shape = generate_transform(source_crs, destination_crs)(shape)

    if dst_affine is not None:
        shape = ops.transform(lambda r, q: dst_affine * (r, q), shape)

    return shape


def azimuthal_from_geometry(geometry):
    """Returns azimuthal equidistant projection centered in geometry.

    """
    centroid_shp = geometry.centroid.get_shape(WGS84_CRS)
    # https://gis.stackexchange.com/a/289923/99665
    aeqd = pyproj.Proj(proj='aeqd', ellps='WGS84', datum='WGS84',
                       lat_0=centroid_shp.y, lon_0=centroid_shp.x)
    aeqd_crs = CRS.from_string(aeqd.srs)

    return aeqd_crs
