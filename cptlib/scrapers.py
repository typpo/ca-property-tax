from collections import deque
import concurrent.futures
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
    self.request_concurrency = 5
    self.request_avg_qps = 2.5

    self.request_error_retries = 6
    # Exponential backoff starting with this number of seconds
    self.request_error_backoff_secs = 2

    self.request_unsuccessful_string = None

  def scrape(self):
    """Execute the scraper. Loop through Parcels and download HTML files.
    """
    count = 0

    futures = set()
    concur = self.request_concurrency
    start_times = deque(maxlen=concur)
    expected_time = concur / max(self.request_avg_qps, 15)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concur) as executor:
      for parcel in self.parcels:
        if len(futures) > concur:
          # wait for at least one thread to be completed. second item is a
          #   set of not_done threads, so should return with a size of MAX - 1
          (done, futures) = concurrent.futures.wait(futures,
              return_when=concurrent.futures.FIRST_COMPLETED)

          for future in done:
            # This will raise any exception that the called function did
            future.result()

          # rough approximation of how long it has taken for the [#] of tasks
          #   to complete
          elapsed_time = time.time() - start_times[0]
          time.sleep(max(expected_time - elapsed_time, 0))

        count += 1

        # There's a lot of overhead to starting a thread and then waiting for
        #   completion so looping through already-created files is extremely
        #   slow. Figure out the path and check for existence of the file
        #   before launching the thread.
        path = os.path.join(self.data_dir, parcel.html_file_path)

        print(count, parcel.apn, path)

        # Check if the file already exists
        if os.path.exists(path):
          print(count, '-> File exists. Skipping')
          continue

        futures.add(executor.submit(self._execute_scrape, count, parcel, path))
        start_times.append(time.time())

  def _execute_scrape(self, count, parcel, path):
    """Do the scraping with retries and backoff

    Args:
        count (int): Iteration number (for logging)
        parcel (Parcel): Parcel we're scraping
        path (str): Path to write HTML file to

    Raises:
        exc: Connection or Timeout exception from requests
    """
    url = self._get_scrape_url(parcel)

    # create the directory(s)
    try:
      os.makedirs(os.path.dirname(path))
    except FileExistsError:
      pass

    request_tries = 0

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
