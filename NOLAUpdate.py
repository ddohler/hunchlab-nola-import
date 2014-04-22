import subprocess
from NOLA2CSV import NOLATransformer, soda_to_hl2_csv


def main():
    headers = ["id", "datasource", "pointx", "pointy", "address", "datetimefrom",
               "datetimeto", "report_time", "class", "last_updated"]
    url = u'http://data.nola.gov/resource/jsyu-nz5r.json'
    outpath = 'NolaCrimes2014.csv'

    print('Downloading data to %s' % outpath)
    soda_to_hl2_csv(url, outpath, headers, NOLATransformer(url))

    print('Uploading data to HunchLab.')
    subprocess.call(['python', 'upload.py', outpath])
    print('Upload complete.')

if __name__ == '__main__':
    main()
