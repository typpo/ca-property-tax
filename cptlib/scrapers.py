import time

class Scraper():
  def __init__(self, parcels_generator, data_dir, url_tpl):
    self.parcels = parcels_generator
    self.data_dir = data_dir
    self.url_tpl = url_tpl


    self.request_type = 'GET'
    self.request_params = {}
    # Be kind to the servers running on 20 year old hardware
    # Minimum delay is 0.1 seconds which is an absolute max of 10 QPS
    self.request_qps = 3

    self.request_error_retries = 6
    self.request_error_backoff_secs = 2

  def scrape(self):
    count = 0
    delay_secs = 1 / self.request_qps

    for parcel in self.parcels:
      count =+ 1

      url = self._scrape_url(parcel)
      path = PATH + parcel.html_file_path

      # create directory
      # check if file exists

      request_tries = 0
      start_time = time.time()

      while True:
        try:
          request_tries += 1
          resp = self._req_make_request(url)

          # Request was successful
          break
        except:
          # Catches network failures
          time.sleep(pow(self.request_error_backoff_secs, request_tries))
          pass


      if self._req_is_success(resp):
        with gzip.open(path, 'wt') as f_out:
          f_out.write(resp.text)

      time.sleep(max(delay_secs - (time.time() - start_time), 0.1))


  def _scrape_url(self, parcel):
    return self.url_tpl.format(apn=parcel.apn)

  def _req_make_request(self, url):
    if self.request_type == 'GET':
      return requests.get(url, **self.request_params)
    else:
      return requests.post(url, **self.request_params)

  def _req_is_success(self, response):
    return response.status_code == 200
