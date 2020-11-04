import gzip
import os
import time

import requests

class Scraper():
  """Scraper class

  This is fairly configurable and probably won't need to be overridden.
  """
  def __init__(self, parcels_generator, data_dir, url_tpl):
    """Generate a scraper instance

    Args:
        parcels_generator (Parcels): Parcels iterator
        data_dir (str): Directory to write HTML files to
        url_tpl (str): URL template. {apn_clean} is replaced at runtime
    """
    self.parcels = parcels_generator
    self.data_dir = data_dir
    self.url_tpl = url_tpl

    # You can change these properties to configure behavior of requests
    self.request_type = 'GET'
    self.request_params = {'headers':
        {'User-Agent': ('CA Property Tax Scraper '
                        '(https://github.com/typpo/ca-property-tax)')}}

    # Be kind to the servers running on 20 year old hardware
    # Minimum delay is 0.1 seconds which is an absolute max of 10 QPS
    self.request_qps = 3

    self.request_error_retries = 6
    # Exponential backoff starting with this number of seconds
    self.request_error_backoff_secs = 2

    self.request_unsuccessful_string = None

  def scrape(self):
    """Execute the scraper. Loop through Parcels and download HTML files.
    """
    count = 0
    delay_secs = 1 / self.request_qps

    for parcel in self.parcels:
      count += 1

      url = self._get_scrape_url(parcel)
      path = os.path.join(self.data_dir, parcel.html_file_path)
      print(count, parcel.apn, path)

      # Check if the file already exists
      if os.path.exists(path):
        print('-> File exists. Skipping')
        continue

      # create the directory
      try:
        os.mkdir(os.path.dirname(path))
      except FileExistsError:
        pass

      request_tries = 0
      start_time = time.time()

      while True:
        try:
          request_tries += 1
          resp = self._req_make_request(url)

          # Request was successful
          break
        except (requests.ConnectionError, requests.Timeout) as exc:
          # Catches network failures
          if request_tries >= self.request_error_retries:
            print('Reached max number of retries')
            raise exc

          time.sleep(pow(self.request_error_backoff_secs, request_tries))
          pass

      if self._req_is_success(resp):
        with gzip.open(path, 'wt') as f_out:
          f_out.write(resp.text)

      else:
        print('-> Request not successful: {}'.format(resp.status_code))

      time.sleep(max(delay_secs - (time.time() - start_time), 0.1))

  def _get_scrape_url(self, parcel):
    """Generate the URL to scrape based on the URL template and Parcel

    Override this if URL generation is more complex.

    Args:
        parcel (Parcel): Current Parcel

    Returns:
        str: Request URL
    """
    return self.url_tpl.format(apn_clean=parcel.apn_clean)


  def _req_make_request(self, url):
    """Make the request given the URL. Uses self.request_type and
    self.request_params.

    Override this if request is more complex.

    Args:
        url (str): URL

    Returns:
        Response: Response object
    """
    if self.request_type == 'GET':
      return requests.get(url, **self.request_params)
    else:
      return requests.post(url, **self.request_params)

  def _req_is_success(self, response):
    """Test if request was successful.

    Override this if it makes sense to check more than response code.

    Args:
        response (Response): Response object

    Returns:
        bool: True if request was "successful"
    """
    return (response.status_code == 200 and
      (not self.request_unsuccessful_string
       or self.request_unsuccessful_string not in response.text))
