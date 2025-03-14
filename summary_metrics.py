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
from arglu.graph_processing import make_arg_dicts_from_graph, make_graph_from_arg_dicts, get_perspectives_dict
# from arglu.mutable_tree import MutableTree
# from arglu.node import Node
# from arglu.plot_argument_graphs import show_graph

import re

def get_alphanum(string):
    return re.sub(r'\W+', '', string)


def normalize_list_data(text_list):
    return [get_alphanum(unicodedata.normalize("NFKD", t)) for t in text_list]


def get_leaves(networkx_graph):
    leaves = [node for node in networkx_graph.nodes() 
            if networkx_graph.out_degree(node) == 1 and 
               networkx_graph.in_degree(node) == 0 ]

    leaf_texts = [networkx_graph.nodes()[leaf]["text"] for leaf in leaves]
    return list(sorted(leaf_texts))


def get_leaf_perspectives(leaf_list, networkx_graph):

    nodes, relations = make_arg_dicts_from_graph(networkx_graph)
    text2node = {t: n for n, t in nodes.items()}
    perspective_dict = get_perspectives_dict(nodes, relations)
    print(perspective_dict)
    import pdb; pdb.set_trace()
    text2perspective = {t: perspective_dict[n] for t, n in text2node.items()}

    return [text2perspective[t] for t in leaf_list]



def get_gold_and_pred_perspectives(gold_graph, pred_graph):
    
    try:
        gold_persp_dict= get_perspectives_dict(*make_arg_dicts_from_graph(gold_graph))
        pred_persp_dict = get_perspectives_dict(*make_arg_dicts_from_graph(pred_graph))
    except:
        nodes, relations = make_arg_dicts_from_graph(pred_graph)
        print(nodes)
        print(relations)
        print("Failed here")
        exit()
        
    gold_persp_dict.pop("main topic")
    pred_persp_dict.pop("main topic")
    gold_keys = list(gold_persp_dict)
    
    gold_perspectives = [gold_persp_dict[k] for k in gold_keys]
    pred_perspectives = [pred_persp_dict.get(k, "black") for k in gold_keys]

    persp_map = {"red":0, "green":1, "black":2}

    pred_perspectives = [persp_map[p] for p in pred_perspectives]
    gold_perspectives = [persp_map[p] for p in gold_perspectives]

    return(gold_perspectives, pred_perspectives)


def node_stance_accuracy(gold, predicted):
    
    gold_perspectives, pred_perspectives = get_gold_and_pred_perspectives(gold_graph=gold, 
                                                            pred_graph=predicted)

    n_correct = sum(np.array(gold_perspectives) == np.array(pred_perspectives))
    n_total = len(gold_perspectives)

    return(n_correct / n_total)


def node_stance_f1(gold, predicted):
    

    gold_perspectives, pred_perspectives = get_gold_and_pred_perspectives(gold_graph=gold, 
                                                            pred_graph=predicted)

    # print(gold_perspectives)
    # print(pred_perspectives)
    # import pdb; pdb.set_trace()
    return f1_score(y_true=gold_perspectives, y_pred=pred_perspectives, average="macro")

def node_confusion_matrix(gold, predicted):
    gold_perspectives, pred_perspectives = get_gold_and_pred_perspectives(gold_graph=gold, 
                                                            pred_graph=predicted)
    return confusion_matrix(y_true=gold_perspectives, y_pred=pred_perspectives,labels=[0,1,2])

def parse_text_to_networkx(text):
    node_re = r"\s*([Cc]omment .+?)\s*\(\s*(\S+)\s*(.+?)\s*\)\s*(.+)"

    text_lines = text.split("\n")
    G = nx.DiGraph(rankdir="TB")

    G.add_node("main topic", node_name="main topic", text="")

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


def node_match(node_1, node_2):
    return node_1["node_name"] == node_2["node_name"]

def compute_node_stance_f1_ged(references, predictions):
    """"""

    node_f1s = []
    geds = []

    for lab, pred in list(zip(references, predictions)):

        gold_graph = parse_text_to_networkx(lab)
        pred_graph = parse_text_to_networkx(pred)
        node_accs.append(node_stance_accuracy(gold=gold_graph, predicted=pred_graph))
        node_f1s.append(node_stance_f1(gold=gold_graph, predicted=pred_graph))
        ged = nx.graph_edit_distance(gold_graph, pred_graph, node_match=node_match)
        geds.append(ged)
        confusion_matrix += node_confusion_matrix(gold=gold_graph, predicted=pred_graph)

    llr = pd.DataFrame({"node_f1":node_f1s, "ged":geds,"len_diff":len_diffs})
    llr.to_csv("low_level_results.csv")
    
    return np.mean(node_f1s), np.mean(geds)



if __name__ == "__main__":
    train_data_path = "data/end_to_end_train_multilevel.csv"
    train_data = pd.read_csv(train_data_path)
    for i, row in train_data.iterrows():
        comments = row["comments"]
        summaries = row["summaries"]
        print(f"Comments: {comments}")
        print(f"Summaries: {summaries}")
        summary_graph = parse_text_to_networkx(row["summaries"])
        nodes, relations = make_arg_dicts_from_graph(summary_graph)
        print(nodes)
        print(relations)
        break
