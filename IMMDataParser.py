import os
import shutil

class IMMDataParser:

    def __init__(self, files_dir_name, node_properties, encoding=None):
        # nodeGen is a generator function that will generate an array representing a node
        if(encoding is None):
            encoding = "utf-8"
        self.encoding = encoding
        self.files_dir_name = files_dir_name
        self.nodes_file_name = files_dir_name + "\\nodes.txt"
        self.graph_file_name = files_dir_name + "\\graph.txt"
        self.attribute_file_name = files_dir_name + "\\attribute.txt"
        self.node_properties = node_properties

    def build_row(self, data):
        row = data[0]
        for attr in data[1:]:
            row = row + "\t" + attr
        row = row + "\n"
        return row

    def create_nodes(self, nodes_gen):
        with open(self.nodes_file_name, "w", encoding=self.encoding) as f:
            for node_data in nodes_gen:
                node = self.build_row(node_data)
                f.write(node)

    def create_attribute_file(self, n, m):
        with open(self.attribute_file_name, "w", encoding=self.encoding) as file:
            file.write("n=" + str(n) + "\n")
            file.write("m=" + str(m) + "\n")

    def format_graph(self, graph_file_name, delimiter=None, header=True, encoding="utf-8", remove_weights=False):
        if (delimiter is None):
            delimiter = "\t"

        n = 0
        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                if(line != "" and line != "\n"):
                    n += 1

        m = 0
        with open(graph_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                if (line != "" and line != "\n"):
                    m += 1

        if(header):
            m -= 1

        self.create_attribute_file(n, m)

        with open(self.graph_file_name, "w", encoding=self.encoding) as f:
            with open(graph_file_name, "r", encoding=encoding) as file:
                if (header):
                    header = file.readline()
                    res = header.strip("\n").split(delimiter)
                    #self.create_attribute_file(int(res[0]), int(res[1]))
                #m = 0
                #d = {}
                for line in file:
                    res = line.strip("\n").split(delimiter)
                    if (len(res) > 1):
                        if(remove_weights):
                            f.write(res[0] + "\t" + res[1] + "\n")
                        else:
                            f.write(line.replace(delimiter, "\t"))
                        #if (not header):
                            #m += 1
                            #d[res[0]] = 0
                            #d[res[1]] = 0
                #if (not header):
                    #n = len(d.keys())
                    #self.create_attribute_file(int(n), int(m))

    def direct_edges(self):
        new_graph_name = self.graph_file_name.split(".")[0] + "_dir.txt"
        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    f2.write(line)
                    res = line.strip("\n").split("\t")
                    if (len(res) > 1):
                        temp = res[0]
                        res[0] = res[1]
                        res[1] = temp
                        f2.write(self.build_row(res))

        with open(self.attribute_file_name, "r", encoding=self.encoding) as f3:
            n = f3.readline().split("=")[1].strip("\n")
            m = f3.readline().split("=")[1].strip("\n")

        with open(self.attribute_file_name, "w", encoding=self.encoding) as f4:
            f4.write("n=" + n + "\n")
            f4.write("m=" + str(2 * int(m)) + "\n")
            f4.close()

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_graph_name)

    def add_default_weights(self, weighted=False):
        if(weighted):
            temp_graph = self.graph_file_name.split(".")[0] + "_temp.txt"
            shutil.copy2(self.graph_file_name, temp_graph)
            self.format_graph(temp_graph, None, False, self.encoding, True)
            os.remove(temp_graph)

        d = {}
        with open(self.graph_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                res = line.strip("\n").split("\t")
                if (len(res) > 1):
                    key = res[1]
                    if (key not in d):
                        d[key] = 0
                    d[key] = d[key] + 1

        temp_graph = self.graph_file_name.split(".")[0] + "_temp.txt"
        with open(self.graph_file_name, "r", encoding=self.encoding) as f:
            with open(temp_graph, "w", encoding=self.encoding) as f2:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (len(res) > 1):
                        key = res[1]
                        f2.write(line.strip("\n") + "\t" + str(1 / d[key]) + "\n")


        with open(temp_graph, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                        for line in f:
                            file.write(line)
        os.remove(temp_graph)

    def remove_nodes_by_property(self, property_name, value, default_weights=False):
        # Remove from nodes file
        removed_nodes = {}
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_rm.txt"

        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:

                ind = 0
                for i in range(len(self.node_properties)):
                    if (self.node_properties[i] == property_name):
                        ind = i
                        break

                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    if (res[ind] != value):
                        f2.write(line)
                    else:
                        removed_nodes[res[0]] = 0

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

        # Remove from graph file
        new_graph_name = self.graph_file_name.split(".")[0] + "_rm.txt"

        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                removed_edges = 0
                for line in f:
                    res = line.split("\t")
                    res = [x.strip("\n") for x in res]
                    if (res[0] not in removed_nodes) and (res[1].strip("\n") not in removed_nodes):
                        f2.write(line)
                    else:
                        removed_edges += 1
                        if (res[0] in removed_nodes):  # res[0] was in both nodes and the graph
                            removed_nodes[res[0]] = 1
                        if (res[1].strip("\n") in removed_nodes):  # res[1] was in both nodes and the graph
                            removed_nodes[res[1]] = 1

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)

        os.remove(new_graph_name)

        f3 = open(self.attribute_file_name, "r")
        n = int(f3.readline().split("=")[1].strip("\n"))
        m = int(f3.readline().split("=")[1].strip("\n"))
        f3.close()

        n -= len({key: val for key, val in removed_nodes.items() if val == 1}.keys())
        m -= removed_edges
        self.create_attribute_file(n, m)

        if (default_weights):
            self.add_default_weights(True)

    def replace_nodes_Ids(self, d):
        new_nodes_name = self.nodes_file_name.split(".")[0] + "_changed.txt"
        deleted_nodes = 0
        deleted_edges = 0
        with open(new_nodes_name, "w", encoding=self.encoding) as f2:
            with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (int(res[0]) in d):
                        res[0] = str(d[int(res[0])])
                        f2.write(self.build_row(res))
                    else:
                        deleted_nodes += 1

        with open(new_nodes_name, "r", encoding=self.encoding) as f:
            with open(self.nodes_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_nodes_name)

        new_graph_name = self.graph_file_name.split(".")[0] + "_changed.txt"

        with open(new_graph_name, "w", encoding=self.encoding) as f2:
            with open(self.graph_file_name, "r", encoding=self.encoding) as f:
                for line in f:
                    res = line.strip("\n").split("\t")
                    if (int(res[0]) not in d) or (int(res[1]) not in d) :
                        deleted_edges += 1
                    else:
                        res[0] = str(d[int(res[0])])
                        res[1] = str(d[int(res[1])])
                        f2.write(self.build_row(res))

        with open(new_graph_name, "r", encoding=self.encoding) as f:
            with open(self.graph_file_name, "w", encoding=self.encoding) as file:
                for line in f:
                    file.write(line)
        os.remove(new_graph_name)

        f3 = open(self.attribute_file_name, "r")
        n = int(f3.readline().split("=")[1].strip("\n"))
        m = int(f3.readline().split("=")[1].strip("\n"))
        f3.close()

        n -= deleted_nodes
        m -= deleted_edges
        self.create_attribute_file(n, m)

    def build_protected_group_dict(self, is_protected):
        d = {}
        protected = 0
        non_protected = 0
        with open(self.nodes_file_name, "r", encoding=self.encoding) as f:
            for line in f:
                res = line.strip("\n").split("\t")
                if (is_protected(res)):
                    protected += 1
                    d[int(res[0])] = (-1) * protected
                else:
                    d[int(res[0])] = non_protected
                    non_protected += 1
        d = {k: (v + protected) for (k, v) in d.items()}
        return protected, d

    def change_protected_Ids(self, is_protected):
        protected_users_num, new_Ids = self.build_protected_group_dict(is_protected)
        self.replace_nodes_Ids(new_Ids)
        with open(self.files_dir_name + "\\protected_group.txt", "w", encoding=self.encoding) as f:
            f.write("R=" + str(protected_users_num))

    def create_lt(self):
        shutil.copy2(self.graph_file_name, self.graph_file_name.split(".")[0] + "_lt.inf")

    def create_ic(self):
        shutil.copy2(self.graph_file_name, self.graph_file_name.split(".")[0] + "_ic.inf")

    def create_input_files(self, nodes_gen, graph_file_name, delimiter=None, header=True, encoding="utf-8", directed=True, weighted=True, add_weights= False, lt=True, ic=True):
        os.mkdir(self.files_dir_name)
        shutil.copy2(graph_file_name, self.files_dir_name + "\\original_graph.txt")
        self.create_nodes(nodes_gen)
        self.format_graph(graph_file_name, delimiter, header, encoding, add_weights)
        if(not directed):
            self.direct_edges()
        if(not weighted) or (add_weights):
            self.add_default_weights(weighted)
        if(lt):
            self.create_lt()
        if (ic):
            self.create_ic()