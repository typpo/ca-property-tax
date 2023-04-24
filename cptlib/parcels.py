import csv
import os
import re

import shapefile
from shapely.geometry import Polygon


def centroidfn_from_latlng(lat_field_name, lng_field_name):
  """Return a centroid function to get lat/long values from a record.
    The function returned will extract the lat/long values (using the keys).

  Args:
      lat_field_name (str): Key (field) name for latitude field
      lng_field_name (str): Key (field) name for latitude field
  """
  def centroid_fn(record):
    return (record[lat_field_name], record[lng_field_name])

  return centroid_fn

def centroidfn_from_shape(shape_field = 'points'):
  """Return a centroid function to get a polygon's centroid from a record.
     The function returned will extract the polygon (using the key) and then
     calculate a centroid.

  Args:
      shape_field (str, optional): Key (field) name for points list. Should be
        'points', which is pulled from the shape file and added to the record.
        Defaults to 'points'.
  """
  def centroid_fn(record):
    points = record[shape_field]
    if not points:
      return None

    centroid_xy = list(Polygon(points).centroid.coords)[0]
    # latitude is y, longitude is x
    return (centroid_xy[1], centroid_xy[0])

  return centroid_fn

class Parcel():
  """Represents a single parcel
  """
  def __init__(self, address, county_code, apn, centroid = None, tax = None):
    self.address = address
    self.county_code = county_code
    self.apn = apn.strip()

    self.centroid = centroid
    self.tax = tax

  @property
  def csv_row(self):
    """Generate a dict representation suitable for being written to CSV

    Returns:
        dict: Parcel as dict
    """
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
    """Generate a relative file path for the parcel's HTML file

    Returns:
        str: Relative file path and name
    """
    apn = self.apn_clean

    # Lots of files in a single directory can cause performance to suffer
    # Create a multi-level directory structure based on APN values
    return os.path.join(apn[0:3], apn[3:6], '{}.htm.gz'.format(apn))

  @property
  def apn_clean(self):
    """Generate a cleaned APN string (only alphanumeric)

    Returns:
        str: Cleaned APN string
    """
    return re.sub(r'[^A-Za-z0-9]', '', self.apn)

class Parcels():
  """Abstract class to generate a Parcels based on a file
  """
  def __init__(self, county_code, apn_column, address_column, centroid_fn):
    """Create a Parcels iterator.

    Args:
        county_code (str): County code
        apn_column (str): Field key for the APN column
        address_column (str): Field key for the address column
        centroid_fn (callable): Function (incl lambda) which will get the row
          (as a dict) and return the centroid as `(lat, lng)`
    """
    self.county_code = county_code
    self.apn_column = apn_column
    self.address_column = address_column
    self.centroid_fn = centroid_fn

    self.length = 0

    self.valid_apn_pattern = None

  def _get_address(self, row):
    """Return address given row and the address_column value

    Override me if getting the address is more complex

    Args:
        row (dict): Row

    Returns:
        str: Address
    """
    return row[self.address_column] if self.address_column else None

  def _record_is_valid_parcel(self, row):
    """Check if the row/record is valid

    In some cases the record doesn't have APN and/or geo info, which
    isn't of use to us, and can cause problems.

    This method can be overridden, but should still be called.

    Args:
        row (dict): Record

    Returns:
        bool: True if record is a valid parcel and should be scraped / parsed
    """
    return (row[self.apn_column]
            and bool(not self.valid_apn_pattern
                or re.search(self.valid_apn_pattern, row[self.apn_column])))

  def _make_parcel(self, row):
    """Return a Parcel from the row and helper methods

    Args:
        row (dict): Row

    Returns:
        Parcel: Parcel
    """
    return Parcel(self._get_address(row), self.county_code,
                  row[self.apn_column], self.centroid_fn(row))

  def __iter__(self):
    """I'm an interator!
    """
    return self

  def __next__(self):
    raise NotImplementedError

  def __len__(self):
    return self.length



class ParcelsCSV(Parcels):
  """Class which generates Parcels from a CSV file.
  """
  def __init__(self, county_code, apn_column, address_column, centroid_fn,
      csv_file_path):
    """Create a Parcels iterator which loops through a CSV file.

    Args:
        county_code (str): County code
        apn_column (str): Field key for the APN column
        address_column (str): Field key for the address column
        centroid_fn (callable): Function (incl lambda) which will get the row
          (as a dict) and return the centroid as `(lat, lng)`
        csv_file_path (str): CSV file path
    """
    super().__init__(county_code, apn_column, address_column, centroid_fn)

    self.csv_file = open(csv_file_path, encoding='utf-8-sig')
    # length is # of rows minus header row
    self.length = sum(1 for line in self.csv_file) - 1

    # reset the file before creating dictreader
    self.csv_file.seek(0)
    self.csv_reader = csv.DictReader(self.csv_file)

  def __next__(self):
    while True:
      row = next(self.csv_reader)

      if self._record_is_valid_parcel(row):
        # If not a valid parcel then keep iterating until we get one
        return self._make_parcel(row)

      print('-> Skipping invalid record')



"""Generate Parcels from a Shapefile.

Pass the APN column key, address column key, a function which returns a
centroid, and the path to the CSV file.

Records must have a polygon shape.
"""
class ParcelsShapefile(Parcels):
  """Class which generates Parcels from a Shapefile
  """
  def __init__(self, county_code, apn_column, address_column, centroid_fn,
      shape_file_path):
    """Create a Parcels iterator which loops through a CSV file.

    Args:
        county_code (str): County code
        apn_column (str): Field key for the APN column
        address_column (str): Field key for the address column
        centroid_fn (callable): Function (incl lambda) which will get the row
          (as a dict) and return the centroid as `(lat, lng)`
        shape_file_path (str): Shapefile path
    """
    super().__init__(county_code, apn_column, address_column, centroid_fn)

    self.sf = shapefile.Reader(shape_file_path)
    self.length = len(self.sf)
    self.idx = 0

    # we only know how to deal with polygons
    assert self.sf.shapeType == shapefile.POLYGON

  def __next__(self):
    while self.idx < len(self.sf):
      record = self.sf.shapeRecord(self.idx)
      self.idx += 1

      # Create a dict from the record and add the polygon points to the dict
      #   with the key 'points'
      dct = record.record.as_dict()
      dct['points'] = record.shape.points

      if self._record_is_valid_parcel(dct):
        # If not a valid parcel then keep iterating until we get one
        return self._make_parcel(dct)

      print('-> Skipping invalid record')

    raise StopIteration

  def _record_is_valid_parcel(self, row):
    """Check if the shapefile record (as a dict) is valid

    In some cases the record doesn't have polygon points

    Args:
        row (dict): Record

    Returns:
        bool: True if record is a valid parcel and should be scraped / parsed
    """
    return bool(row['points']
                and super()._record_is_valid_parcel(row))
