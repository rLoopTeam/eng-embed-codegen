import yaml
from collections import OrderedDict

# @see http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
def yaml_ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

# usage example:
# yaml_ordered_load(stream, yaml.SafeLoader)

def yaml_ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    class OrderedDumper(Dumper):
        pass
    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)

# usage:
# yaml_ordered_dump(data, Dumper=yaml.SafeDumper)


with open("../templates/test.yaml", 'r') as stream:
    try:
        data = yaml_ordered_load(stream, yaml.SafeLoader)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


class CStructTemplate:
   
    def __init__(self):
        print "INITIALIZING CStructTemplate"
        self.name = ""
        self.typename = ""
        self.desc = ""
        self.elements = []  # non-struct members
        self.children = []  # substructures
        
    def __str__(self):
        return self.str()
    
    def str(self, level=0):
        indent_prefix = "    "
        indent = indent_prefix * level
        s = []
        s.append("{}Name: {}".format(indent, self.name))
        s.append("{}Desc: {}".format(indent, self.desc))
        s.append("{}Typename: {}".format(indent, str(self.typename)))
        s.append("{}Elements:".format(indent))
        for element in self.elements:
            s.append("{}".format(element.str(level + 1)))
        s.append("{}Children:".format(indent))
        for child in self.children:
            s.append("{}".format(child.str(level + 1)))
        return "\n".join(s)
    
class CVarTemplate:
    def __init__(self, name=None, desc=None, type=None):
        self.name = name
        self.desc = desc
        self.type = type

    def __str__(self):
        return self.str()

    def str(self, level=0):
        indent_prefix = "    "
        indent = indent_prefix * level
        return "{}(name: {}; type: {}, desc: {})".format(indent, self.name, self.type, self.desc)
        

def is_dict(value):
    return isinstance(value, (dict, OrderedDict))
    
def is_list(value):
    return isinstance(value, list)  # Maybe add tuple in here?

def read_yaml_struct(key, data):

    s = CStructTemplate()
    s.name = key
    s.desc = data.get("desc", None)
    s.typename = data.get("typename", None)

    for k, v in data.iteritems():
        print "k, v: {} {}".format(k, v)
        if k in ["name", "desc", "typename"]:
            continue
        if is_dict(v):
            # It's a substructure
            print "Found substructure {}".format(k)
            s.children.append(read_yaml_struct(k,v))
        elif is_list(v):
            print "Found an element {} {}".format(k, v)
            # It's an element
            s.elements.append(read_yaml_var(k, v))
        else:
            print "ERROR: Not sure what to do with {}: {}".format(k, v)

    """
    s = CStructTemplate()
    s.name = key
    s.desc = data.get("desc", None)
    s.typename = data.get("typename", None)
    for k, v in data.iteritems():
        print "Processing kv {}  {}".format(k, v)
        # If the dictionary item is a dict, it's a substructure
        if is_dict(v):            
            for k1, v1 in v.iteritems():
                s.children.append(read_yaml_struct(k1, v1))
        else:            
            s.elements.append(read_yaml_var(k, v))

    return s
    """ 
    return s
    
def read_yaml_var(var, data):
    v = CVarTemplate()
    v.name = var
    v.desc = data[0]
    v.type = data[1]
    return v


def read_yaml_structs(data):
    # Root is always a dict
    structs = []
    for key, value in data.iteritems():
        print "structs: reading {}".format(key)
        s = read_yaml_struct(key, value)
        """
        s = CStructTemplate()
        s.name = key
        s.desc = value.get("desc", None)
        s.typename = value.get("typename", None)
        for k, v in value.iteritems():
            if k in ["name", "desc", "typename"]:
                continue
            if is_dict(v):
        """
        """
        if is_dict(value):
            cstruct = read_yaml_struct(key, value)
            out.append(cstruct)
        else:
            out.append(read_yaml_var(key, value))
        """
        structs.append(s)
    return structs


import pprint
d = read_yaml_structs(data['structs'])
for i in d:
    print i
