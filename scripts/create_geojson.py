import argparse
import csv
import json

class CSVReader(object):

    def __init__(self, csvpath):

        self.reader = csv.reader(open(csvpath, "r"))
        self.header = self.reader.next()
        self.ncols = len(self.header)

    def __iter__(self):

        return self

    def next(self):

        item = {}
        row = self.reader.next()

        for k in range(self.ncols):
            item[self.header[k]] = row[k]

        return item


if __name__ == "__main__":

    # Handle and parse the input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("csvpath", help="earthquake csv file path")
    parser.add_argument("jsonpath", help="geojson file path")
    args = parser.parse_args()

    csvreader = CSVReader(args.csvpath)

    # Create the GeoJSON Feature Collection
    featureCollection = {"type": "FeatureCollection"}
    featureList = []

    for item in csvreader:
        
        feature = {
            "type": "Feature",
            "properties": {
                "magnitude": float(item["Magnitude"]),
                "datetime": item["DateTime"],
                "depth": float(item["Depth"])
            },
            "geometry": {
                "type": "Point",
                "coordinates": [float(item["Longitude"]), float(item["Latitude"])]
            }
        }

        featureList.append(feature)

    featureCollection["features"] = featureList

    # Save the features in the GeoJSON file.
    jsonfile = open(args.jsonpath, "w")
    json.dump(featureCollection, jsonfile, indent=2, sort_keys=True)
    jsonfile.close()





