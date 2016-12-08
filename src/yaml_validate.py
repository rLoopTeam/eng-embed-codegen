import yaml
import pprint

with open("../templates/test.yaml", 'r') as stream:
    try:
        print yaml.dump( yaml.load(stream))
    except yaml.YAMLError as exc:
        print(exc)