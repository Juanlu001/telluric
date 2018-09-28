from shapely.ops import split
from shapely.geometry import Polygon, GeometryCollection

from telluric.constants import WGS84_CRS, WEB_MERCATOR_CRS
from telluric.vectors import GeoVector, MERCATOR_WIDTH, ANTIMERIDIAN


def offset_shape(shp, x_offset=MERCATOR_WIDTH, y_offset=0.0):
    # TODO: Handle polygons with holes and non-polygons
    new_exterior = []
    for x, y in shp.exterior.coords:
        new_exterior.append((x - x_offset, y - y_offset))

    return Polygon(new_exterior)


def cut_by_antimeridian(geometry):
    # TODO: Support shapes that cross the meridian several times (really wide ones)
    crs = geometry.crs
    shapes_col = split(geometry.get_shape(crs), ANTIMERIDIAN.get_shape(crs))

    if len(shapes_col) == 1:
        return geometry
    else:
        new_shape = GeometryCollection([
            shapes_col[0], offset_shape(shapes_col[-1])
        ])

        return GeoVector(new_shape, crs)
