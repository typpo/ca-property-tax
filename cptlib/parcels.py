def centroid_from_latlng(lat_field_name, lng_field_name):
  def centroid_fn(record):
    return (record[lat_field_name], record[lng_field_name])

  return centroid_fn



def centroid_from_shape(shape_field = 'points'):
  def centroid_fn(record):
    list(Polygon(coords).centroid.coords)[0]
    poly = Poly(record[shape_field])
    return (poly.lat, poly.lng)

  return centroid_fn


import os
import re

class Parcel:
  def __init__(self, address, county_code, apn, centroid = None, tax = None):
    self.address = address
    self.county_code = county_code
    self.apn = apn

    self.centroid = centroid
    self.tax = tax

  @property
  def csv_row(self):
    return {
        'address': self.address,
        'apn': self.apn,
        'latitude': self.centroid[0],
        'longitude': self.centroid[1],
        'tax': self.tax,
        'county': self.county_code,
    }

  @property
  def html_file_path(self):
    apn = re.sub(r'[^A-Za-z0-9]', self.apn, '')
    return os.path.join('data', apn[0:3], apn[3:6], '{}.html.gz'.format(apn))

import os

class Parcels():
  def __init__(self, county_code, apn_column, address_column, centroid_fn):
    self.county_code = county_code
    self.apn_column = apn_column
    self.address_column = address_column
    self.centroid_fn = centroid_fn

  def _get_address(self, row):
    return row[self.address_column]

  def _make_parcel(self, row):
    return Parcel(self._get_address(row), self.county_code,
                  row[self.apn_column], self.centroid_fn(row))

  def __iter__(self):
    return self



import csv

class ParcelsCSV(Parcels):
  def __init__(county_code, apn_column, address_column, centroid_fn,
      csv_file_path):
    super().__init__(self, county_code, apn_column, address_column, centroid_fn)

    self.csv_reader = dictreader(csv_file_path)

  def __next__(self):
    row = next(self.csv_reader)

    return self._make_parcel(row)



import shapefile

class ParcelsShapeFile(Parcels):
  def __init__(county_code, apn_column, address_column, centroid_fn,
      shape_file_path):
    super().__init__(self, county_code, apn_column, address_column, centroid_fn)

    self.sf = shapefile.Reader(shape_file_path)
    self.idx = 0

    # we only know how to deal with polygons
    assert self.sf.shapeType == shapefile.POLYGON

  def __next__(self):
    if self.idx < len(self.sf):
      record = self.sf.shapeRecord(self.idx)
      self.idx += 1

      dct = record.record.as_dict()
      dct['points'] = record.shape.points
      return self._make_parcel(dct)

    raise StopIteration

    row = next(self.csv_reader)

    return self._make_parcel(row)






