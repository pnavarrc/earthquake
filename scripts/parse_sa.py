import argparse
import csv
import json

# Region of interest
MIN_LAT, MAX_LAT = -64.7754, -16.0458
MIN_LON, MAX_LON = -78.1348, -56.6078

class CSVReader(object):

    def __init__(self, csvpath):

        self.reader = csv.reader(open(csvpath, "r"))
        self.header = map(lambda x: x.strip(), self.reader.next())
        self.ncols = len(self.header)

    def __iter__(self):

        return self

    def next(self):

        item = {}
        row = self.reader.next()

        for k in range(self.ncols):
            item[self.header[k]] = row[k].strip()

        return item

def in_region(lat, lon):

    in_lat = MIN_LAT <= lat <= MAX_LAT
    in_lon = MIN_LON <= lon <= MAX_LON

    return in_lat and in_lon

def try_parse(string):

    number = 0

    try:
        if string.isdigit():
            number = long(string)
        else:
            number = float(string)
    except ValueError:
        return False

    return number

def parse_date(year, month, day):

    y = try_parse(year)
    m = try_parse(month)
    d = try_parse(day)

    if not (y and m and d):
        return False

    return "{m}/{d}/{y}".format(y=y, m=m, d=d)

def parse_time(time_string):

    hh = try_parse(time_string[0:2])

    if not hh:
        hh = "00"

    mm = time_string[2:4]

    if not mm:
        mm = "00"

    ss = time_string[4:6]

    if not ss:
        ss = "01"

    return "{hh}:{mm}:{ss}".format(hh=hh, mm=mm, ss=ss)

if __name__ == "__main__":

    # Handle and parse the input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("csvpath", help="earthquake csv file path")
    parser.add_argument("jsonpath", help="geojson file path")
    args = parser.parse_args()

    csvreader = CSVReader(args.csvpath)

    featureList = []
    for item in csvreader:
        
        skip = False

        # Parse the earthquake data
        lat = float(item["Latitude"])
        lon = float(item["Longitude"])
        mag = try_parse(item["Magnitude"])
        dep = try_parse(item["Depth"])

        if not dep:
            dep = -1

        skip = skip or not in_region(lat, lon)         
        skip = skip or not mag

        if not skip:
            date = parse_date(item["Year"], item["Month"], item["Day"])
            time = parse_time(item["TimeUTC"])
            
            feature = {
                "type": "Feature",
                "properties": {
                    "magnitude": mag,
                    "datetime": "{date} {time}".format(date=date, time=time),
                    "depth": dep
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                }
            }

            featureList.append(feature)
        
    # Create the GeoJSON Feature Collection
    featureCollection = {"type": "FeatureCollection"}
    featureCollection["features"] = featureList

    # Save the features in the GeoJSON file.
    jsonfile = open(args.jsonpath, "w")
    json.dump(featureCollection, jsonfile, indent=2, sort_keys=True)
    jsonfile.close()









