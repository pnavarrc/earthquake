import argparse
import dateutil.parser
import json

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input json file')
    args = parser.parse_args()

    data = json.load(open(args.input, 'r'))
    items = data['features']

    for item in items:
        properties = item['properties']
        dtime = dateutil.parser.parse(properties['datetime'])
        properties['datetime'] = dtime.isoformat()
        item['properties'] = properties

    json.dump(data, open(args.input, 'w'), sort_keys=True)
