from pathlib import Path

import networkx as nx
import os
import ntpath

from application.parsers.gauge_parser import gauge_parser
from application.graph.graph_renderer import GraphRenderer


class Graph_generator:
    def __init__(self, config):
        self.config = config
        self.parser = gauge_parser()
        self.renderer = GraphRenderer(config)

    def generate_spec_graph(self, input_file):
        filename = ntpath.basename(input_file)
        output = self.config.OUTPUT_DIR
        scenarios = self.parser.parse_spec(input_file)
        print("------SCENARIOS-------")
        print(scenarios)
        graph = nx.MultiDiGraph()
        for scenario in scenarios:
            graph.add_node(f"Scenario:{scenario.name}", source_file=scenario.source_file, smell=False, smell_names=list())
            for i, step in enumerate(scenario.steps):
                graph.add_node(f"Step:{step}", smell=False, smell_names=list())
                graph.add_edge(f"Scenario:{scenario.name}", f"Step:{step}", label=i + 1)
                if scenario.web!= "null":
                    print(scenario.web)
                    graph.add_node(f"ServerSide:{scenario.web}", smell=False, smell_names=list())
                    graph.add_edge(f"Step:{step}", f"ServerSide:{scenario.web}", label=i + 1 )

        nx.write_yaml(graph, f"{output}/{filename}.yaml")
        return filename

    def generate_cpt_graph(self, inputfile):
        output = self.config.OUTPUT_DIR
        concepts = self.parser.parse_cpt(inputfile)
        rfile = os.path.basename(inputfile)
        resourceFile = True
        resource =  os.path.splitext(rfile)[0]
        clientObjects = ''
        print("here")
        print(self.config.rpath + r"\\" + resource + r".json")
        try:
            #new_path = os.path.dirname(r'C://Users//camer//Documents//GaugeDepend//samples_test_suites//GmailGaugeTestSuite//src//test//resources//elementValues//'' + resource + '.json')
            clientObjects = self.parser.parse_resource(Path(self.config.rpath + r"\\" + resource + r".json"))
        except FileNotFoundError:
            resourceFile = False

        name = ntpath.basename(inputfile)
        graph = nx.MultiDiGraph()
        for concept in concepts:
            graph.add_node(f"Step:{concept.name}", smell=False, smell_names=list())
            for i, step in enumerate(concept.steps):
                graph.add_node(f"Step:{step}", smell=False, smell_names=list())
                graph.add_edge(f"Step:{concept.name}", f"Step:{step}", label=i + 1)
                if concept.web != "null":
                    graph.add_node(f"ServerSide:{concept.web}", smell=False, smell_names=list())
                    graph.add_edge(f"Step:{step}", f"ServerSide:{concept.web}", label=i + 1 )
                if resourceFile:
                    for k,v,t in zip(clientObjects.keys, clientObjects.values, clientObjects.types):
                        if k in step:
                            keyString = f"{k}" + '\n' + f"{t}: {v}"
                            print(keyString)
                            graph.add_node(f"Client:{keyString}", smell=False, smell_names=list())
                            graph.add_edge(f"Step:{concept.name}", f"Client:{keyString}", label=i + 1 )
                            if k in concept.web:
                                graph.add_edge(f"Client:{keyString}", f"ServerSide:{concept.web}", label=i + 1 )
        nx.write_yaml(graph, f"{output}/{name}.yaml")

        return name

    def parse_folder(self, filepath):
        filenames = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                try:
                    path = subdir + os.sep + file
                    if path.endswith(".spec"):
                        filenames.append(self.generate_spec_graph(path))
                    elif path.endswith(".cpt"):
                        filenames.append(self.generate_cpt_graph(path))
                except Exception as ex:
                    print(f"Error Processing file {path}")
                    print(f"Exception was {ex}")
        return filenames

    def combine_graphs(self, filenames):
        output = self.config.OUTPUT_DIR
        graphs = []
        for filename in filenames:
            g = nx.read_yaml(f"{output}/{filename}.yaml")
            graphs.append(g)
        combined = nx.compose_all(graphs)
        return combined

    def render_graph(self, comnined):
        self.renderer.render_graph(comnined)

    def stabilize(self):
        self.renderer.stabilizer()


if __name__ == "__main__":
    pass
