from collections import defaultdict
import numpy as np
import os
import re
import os.path as op
import pandas as pd
import unicodedata
from sklearn.metrics import f1_score, confusion_matrix
from arglu.plot_argument_graphs import show_graph

import networkx as nx

# from arglu.file_type_utils import read_textgraph, write_textgraph
from arglu.graph_processing import make_arg_dicts_from_graph


def parse_text_to_networkx(text,main_topic=""):
    node_re = r"\s*([Cc]omment .+?)\s*\(\s*(\S+)\s*(.+?)\s*\)\s*(.+)"

    text_lines = text.split("\n")
    G = nx.DiGraph(rankdir="TB")

    G.add_node("main topic", node_name="main topic", text=main_topic)

    colon_trans = str.maketrans("","",":")

    for line in text_lines:
        match_obj = re.match(node_re, line)
        if match_obj:

            node_name, relation, parent, comment = match_obj.groups()
            node_name = node_name.strip().lower()
            relation = relation.strip().lower()
            parent = parent.strip().lower()
            comment = comment.strip().lower()
            
            if (parent in G) and (parent != node_name) and (node_name not in G):
                G.add_node(node_name, node_name=node_name.translate(colon_trans), text=comment.translate(colon_trans))
                G.add_edge(node_name, parent, label=relation.translate(colon_trans))

    return G


if __name__ == "__main__":
    train_data_path = "data/end_to_end_train_multilevel.csv"
    train_data = pd.read_csv(train_data_path)
    #Loads in a csv "file with the columns "comments" and "summaries".
    #Each row contains a list of comments and a corresponding argument graph
    #The "Comments" rows contain numbered lists of comments separated by two newlines
    #The "summaries" column contains the corresponding summaries, and also the argumentative relations between the comments. 

    for i, row in train_data.iterrows():

        comments = row["comments"]
        summaries = row["summaries"]
        
        print(f"COMMENTS:\n\n {comments}\n\n")
        print(f"SUMMARIES:\n\n{summaries}\n\n")

        main_topic = comments.split("\n")[0].split(":")[1].strip()
        summary_graph = parse_text_to_networkx(summaries, main_topic=main_topic)
        # Parses the text in "summaries" to a networkx graph

        nodes, relations = make_arg_dicts_from_graph(summary_graph)
        #converts the networkx graph to a dictionary containing the summaries, and a list showing the relations between the summaries
    
        print(f"NODES:\n\n {nodes}\n\n")
        print(f"RELATIONS:\n\n {relations}\n\n")
        break
