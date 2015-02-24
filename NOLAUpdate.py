import logging
import subprocess
from NOLA2CSV import NOLATransformer, soda_to_hl2_csv


def main():
    headers = ["id", "datasource", "pointx", "pointy", "address", "datetimefrom",
               "datetimeto", "report_time", "class", "last_updated"]
    url = u'https://data.nola.gov/resource/w68y-xmk6.json'
    outpath = 'NolaCrimes2015.csv'

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')

    logging.info('Downloading data to %s' % outpath)
    soda_to_hl2_csv(url, outpath, headers, NOLATransformer(url))

    logging.info('Uploading data to HunchLab.')
    subprocess.call(['python', 'upload.py', outpath])
    logging.info('Upload complete.')

if __name__ == '__main__':
    main()
