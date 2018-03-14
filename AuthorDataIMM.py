from DataParser import DataParser
from geotext import GeoText
from DataUtils import*
from IMMDataParser import IMMDataParser

def build_index_id_dict():
    d = {}
    with open("AMinerCoauthor.dict", "r") as f:
        for line in f:
            res = line.split("\t")
            key = int(res[0])
            value = int(res[1].strip("\n"))
            d[key] = value

    return d


def build_consecutive_id_dict(nodes_file_name):
    d = {}
    i = 0
    with open(nodes_file_name, "r", encoding="utf-8") as f:
        for line in f:
            res = line.strip("\n").split("\t")
            if(len(res) >= 1):
                d[int(res[0])] = i
                i += 1

    return d

def read_author(f):
    lines = [""]*10
    i = 0
    with open(f, encoding="utf-8") as file:
        for line in file:
            lines[i] = line
            i = (i + 1)%10
            if(i == 0):
                yield lines
        if(i > 0):
            yield lines

def parse_author_attr(lines):
    properties = ["Id", "Name", "Affiliation", "Country", "H-index"]

    split_array = lines[0].split(" ")
    if(split_array[1].strip("\n") != ""):
        properties[0] = split_array[1].strip("\n")

    split_array = lines[1].split(" ", 1)
    if(split_array[1].strip("\n") != ""):
        properties[1] = split_array[1].strip("\n")

    split_array = lines[2].split(" ", 1)
    if (split_array[1].strip("\n") != ""):
        properties[2] = split_array[1].strip("\n")

    places = GeoText(lines[2])
    if(len(places.countries) > 0):
        properties[3] = places.countries[0]

    #properties[3] = find_country_in_string(lines[2])

    split_array = lines[5].split(" ", 1)
    if (split_array[1].strip("\n") != ""):
        properties[4] = split_array[1].strip("\n")

    return properties

def author_gen(f):
    reader = read_author(f)
    for lines in reader:
        node_attr = parse_author_attr(lines)
        yield node_attr

# Replace Ids in nodes file only
def replace_Ids(d, nodes_file_name, delimiter=None, new_nodes_name=None):
    removed_nodes = 0
    copy = True
    if(new_nodes_name is None):
        copy = False
        new_nodes_name = nodes_file_name.split(".")[0].strip("\n") + "_changed.txt"
    if(delimiter is None):
        delimiter = "\t"

    f2 = open(new_nodes_name, "w", encoding="utf-8")
    f = open(nodes_file_name, "r", encoding="utf-8")

    for line in f:
        res = line.split(delimiter)
        if(int(res[0]) in d):
            f2.write(line.replace(res[0], str(d[int(res[0])])))
        else:
            removed_nodes += 1

    f2.close()
    f.close()

    f3 = open("input_files_IMM\\attribute.txt", "r")
    n = f3.readline().split("=")[1].strip("\n")
    m = f3.readline().split("=")[1].strip("\n")
    f3.close()

    f4 = open("input_files_IMM\\attribute.txt", "w")
    f4.write("n=" + str(int(n) - removed_nodes)+ "\n")
    f4.write("m=" + m + "\n")
    f4.close()


    if (not copy):
        with open(new_nodes_name, "r", encoding="utf-8") as f:
            with open(nodes_file_name, "w", encoding="utf-8") as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)


def is_protected_country(res):
        if(res[3] == "India"):
            return True
        return False

'''
with open("AMiner-Author.txt", "r+", encoding="utf-8") as f:
    with open("AMiner-Author - Copy.txt", "w", encoding="utf-8") as f2:
        for line in f:
            if("USA" in line):
                f2.write(line.replace("USA", "United States"))
            else:
                f2.write(line)
'''

parser = IMMDataParser("input_files_IMM", ["Id", "Name", "Affiliation", "Country", "H-index"])
parser.create_input_files(author_gen("AMiner-Author - Copy.txt"), "AMinerCoauthor.graph", delimiter=None, header=True, encoding="utf-8", directed=False, weighted=True, add_weights= True, lt=True, ic=True)
replace_Ids(build_index_id_dict(), parser.nodes_file_name)
parser.remove_nodes_by_property("Affiliation", "Affiliation", True)
parser.remove_nodes_by_property("H-index", "0", True)
parser.replace_nodes_Ids(build_consecutive_id_dict("input_files_IMM\\nodes.txt"))
parser.change_protected_Ids(is_protected_country)
parser.create_lt()
parser.create_ic()
