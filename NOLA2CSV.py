import csv
import datetime
import logging
from pytz import timezone
import requests
import time


class NOLATransformer(object):
    """Transforms New Orleans Calls for Service from Socrata Open Data API to HunchLab2 CSV.
    Fields:
        datasource: Name of the datasource to be used in HunchLab2 CSV.
    """

    def __init__(self, datasource):
        self.datasource = datasource

    # Helper functions
    def _decode_address(self, record):
        """Decodes addresses returned as JSON strings (inside the JSON response)."""
        return record[u"block_address"] + u", " + record[u'zip']

    def _convert_time(self, time_str):
        """Adds timezone info to event times and returns properly formatted string"""
        # Dates don't have leading zeroes, so we need to extract them, pad, and
        # reassemble.
        parts = time_str.split(u'/')
        month = parts[0].zfill(2)
        day = parts[1].zfill(2)
        rest = parts[2]
        hhmmss = rest.split()[1]
        if len(hhmmss) == 4:  # E.g. 2:36
            hhmmss = hhmmss.zfill(5)

        clean_str = month + u'/' + day + u'/' + rest.split()[0] + u' ' + hhmmss
        try:
            struct_time = time.strptime(clean_str, '%m/%d/%Y %H:%M:%S')
        except ValueError:
            struct_time = time.strptime(clean_str, '%m/%d/%Y %H:%M')
        central = timezone('US/Central')
        aware_time = central.localize(datetime.datetime(*struct_time[:6]))

        return aware_time.isoformat()

    def transform(self, incident):
        """Converts NOLA crime data to HunchLab2 CSV format.
        Args:
            incident: A dict representing an incident from NOLA's police calls for service API.
        Returns:
            A dict in HunchLab2 Event CSV format.
        """
        row = dict()
        row["id"] = incident[u'nopd_item']
        row["datasource"] = self.datasource
        row["pointx"] = incident[u"mapx"]
        row["pointy"] = incident[u"mapy"]
        row["address"] = self._decode_address(incident)
        row["datetimefrom"] = self._convert_time(incident[u'timecreate'])
        row["datetimeto"] = self._convert_time(incident[u'timecreate'])
        row["report_time"] = self._convert_time(incident[u'timecreate'])
        row["class"] = incident[u'typetext']
        row["last_updated"] = self._convert_time(incident[u'timeclosed'])
        return row


def soda_to_hl2_csv(endpoint_root, outpath, headers, transformer):
    """Downloads all records from a Socrata Open Data API and writes them to a CSV file.

    Args:
        endpoint_root: Socrata open data API endpoint (e.g.
                       http://data.nola.gov/resource/5fn8-vtui.json)
        outpath: Path to the file to write results to
        headers: An array of strings representing the headers in the output CSV. These will be
                 written in the order given as the first line in the CSV.
        transformer: A class exposing a transform() method which consumes a dict representing
                     one record from a Socrata response, and outputs a dict representing a row
                     in the output CSV. This dict will be fed to a csv.DictWriter. The fields
                     in the dict must match those in headers.
    """
    endpoint = endpoint_root + u"?$offset=%s&$limit=%s"

    with open(outpath, "wb") as outfile:
        csv_writer = csv.DictWriter(outfile, headers, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()
        # Loop initialization
        limit = 1000
        offset = 0
        while True:  # Break out if zero results.
            logging.info('%s records processed.' % offset)
            req = requests.get(endpoint % (offset, limit))
            req.raise_for_status()

            data = req.json()
            if len(data) == 0:
                break

            for incident in data:
                try:
                    row = transformer.transform(incident)
                    csv_writer.writerow(row)
                except KeyError:
                    pass

            offset += limit
            time.sleep(0.25)


def main():
    """ Download from all endpoints """
    headers = ["id", "datasource", "pointx", "pointy", "address", "datetimefrom",
               "datetimeto", "report_time", "class", "last_updated"]
    sources = [
        #(u"http://data.nola.gov/resource/28ec-c8d6.json", "NolaCrimes2011.csv"),
        #(u"http://data.nola.gov/resource/rv3g-ypg7.json", "NolaCrimes2012.csv"),
        #(u"http://data.nola.gov/resource/5fn8-vtui.json", "NolaCrimes2013.csv"),
        (u"http://data.nola.gov/resource/jsyu-nz5r.json", "NolaCrimes2014.csv"),
    ]

    for url, outpath in sources:
        # Using the URL as the datasource.
        soda_to_hl2_csv(url, outpath, headers, NOLATransformer(url))


if __name__ == '__main__':
    main()
