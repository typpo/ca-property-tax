def Parser():
  def __init__(self, parcels_generator, data_dir):
    self.parcels = parcels_generator
    self.data_dir = data_dir

    fieldnames = ['address', 'apn', 'longitude', 'latitude', 'tax', 'county']
    self.csv_writer = csv.DictWriter(f_out, fieldnames=fieldnames)

  def parse(self):
    count = 0

    for parcel in self.parcels:
      count += 1

      html_path = self.data_dir + parcel.html_file_path

      with gzip.open(html_path):
        if parse_html(parcel, html):
          self.csv_writer.write_row(parcel.csv_row)
        else:
          pass


  def _parse_html(self, html):
    raise NotImplementedError

class ParserMegabyte(Parser):
  def _parse_html(self, html):
    soup = BeautifulSoup(html, 'html.parser')

    #extract payment info
    tab1 = soup.find('div', {'id':'h2tab1'})
    total_tax = -1
    if tab1 != None:
        bills = tab1.find_all('dt',text='Total Due')

        if len(bills) == 3:
            #grab the total annual payment, not the 6-month one
            #no need to double value later on
            total_tax_str = bills[2].findNext('dd').string.replace('$', '').replace(',', '')
            try:
                total_tax = float(total_tax_str)
            except:
                print('--> Could not parse float', amount_str)
        else:
            print("bad tax records on parcel ",apn)

    else:
        print(apn,"Tax data not available.")


    #extract address
    tab2 = soup.find('div', {'id':'h2tab2'})
    if tab2 is not None:
        address = tab2.find('dt',text='Address').findNext('dd').string

    if address is None:
        address = "UNKNOWN"

    print(address,total_tax)
