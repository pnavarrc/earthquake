import argparse
import json

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input json file')
    args = parser.parse_args()

    data = json.load(open(args.input, 'r'))
    json.dump(data, open(args.input, 'w'))
