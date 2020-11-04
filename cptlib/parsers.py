import csv
import gzip
import os

from bs4 import BeautifulSoup


class Parser():
  """Abstract Parser class.

  Should be overridden to implement specific tax amount parsing routine
  """
  def __init__(self, parcels_generator, data_dir):
    """Generate a Parser instance

    Args:
        parcels_generator (Parcels): Parcels iterator
        data_dir (str): Directory to read HTML files from and write output CSV
    """
    self.parcels = parcels_generator
    self.data_dir = data_dir

    csv_file_path = os.path.join(data_dir, 'output.csv')
    self.csv_file = open(csv_file_path, 'w')
    csv_fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax',
                      'county']
    self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=csv_fieldnames)

  def parse(self):
    """Execute the parser. Loop through Parcels and parse local HTML files.
    """
    count = 0

    for parcel in self.parcels:
      count += 1
      path = os.path.join(self.data_dir, parcel.html_file_path)

      print(count, path)

      try:
        with gzip.open(path, 'rt') as f_in:
          html = f_in.read()
      except FileNotFoundError:
        print(count, '-> HTML file not found')
        continue

      if self._parse_html(parcel, html):
        self.csv_writer.writerow(parcel.csv_row)

        if count % 500 == 0:
          # Flush to filesystem every 500 rows
          self.csv_file.flush()

        continue

      print(count, '-> Could not parse file')

  def _parse_html(self, parcel, html):
    """Should be overridden with specific parsing logic
    """
    raise NotImplementedError

class ParserMegabyte(Parser):
  """Parser class that parses property tax pages hosted by
     Megabyte (mptsweb.com)
  """
  def _parse_html(self, parcel, html):
    """Parse HTML from Megabyte and update the Parcel with tax amount

    Args:
        parcel (Parcel): Parcel associated with HTML text
        html (str): Property tax page HTML

    Returns:
        bool: True if parsing was successful
    """
    soup = BeautifulSoup(html, 'html.parser')

    #extract payment info
    tab1 = soup.find('div', {'id': 'h2tab1'})
    total_tax = -1

    if tab1 != None:
      bills = tab1.find_all('dt', text='Total Due')

      if len(bills) == 3:
        #grab the total annual payment, not the 6-month one
        #no need to double value later on
        total_tax_str = bills[2].findNext('dd').string\
          .replace('$', '').replace(',', '')
        try:
          total_tax = float(total_tax_str)
          # set tax amount on parcel
          parcel.tax = round(total_tax, 2)

          return True
        except:
          print('--> Could not parse float')
      else:
          print("--> bad tax records on parcel")

    return False
