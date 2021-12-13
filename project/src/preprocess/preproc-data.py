#!/usr/bin/env python3

# File: preproc-data.py
# Author: Vincent Chung <vwchung2@illinois.edu>
# Course: CS519 - Scientific Visualization (Fall 2021)
# Assignment: Course Project

import argparse
import os
import json
from datetime import datetime, timedelta

import pandas as pd
from colorhash import ColorHash

parser = argparse.ArgumentParser(
    description='Preprocess the network dataset for graph visualization ' \
        'rendering.')
parser.add_argument('-o', '--output-file', dest='output_fn',
    default='network-graph.json',
    help='Output file name of the JSON file')
parser.add_argument('-t', '--timestamp', dest='timestamp',
    help='Timestamp of instantaneous flow snapshot in ' \
        '"%d/%m/%Y%H:%M:%S" format, defaults to first start time')
parser.add_argument('-n', '--flows-limit', dest='flows_limit',
    type=int, default=0,
    help='If specified, randomly samples up to that many flows (=edges)')
parser.add_argument('input_fn',
    help='The network dataset to process')

# Canvas graph styles template
styles_tmpl = {
    'node': {
        'label': { 'hideSize': 16 }
    },
    'client': {
        'texture': 'images/icons8-computer-64.png',
        'minSize': 24,
    },
    'switch': {
        'texture': 'images/icons8-router-64_blue.png',
        'minSize': 24,
    },
    'edge': {
        'type': 'dotted',
        'animateType': 'gradient',
        # 'animateColor': 'rgb(255,0,0)',
    }
}

# General-purpose clamp function
def clamp(min_val, val, max_val):
    return max(min_val, min(val, max_val))

# General-purpose scale function
def scale1toN(val, min_val, max_val, N):
    return clamp(1, round((N-1.0)* ((val - min_val) / (max_val - min_val))) + 1, N)

# Create RGB triplet string from tuple
def toRGBStr(rgb):
    return f'rgb({rgb[0]}, {rgb[1]}, {rgb[2]})'

# Load the network dataset CSV file as a Pandas DataFrame
def load_csv(csv_fn):
    print(f'Loading CSV input file: {csv_fn}')

    df = pd.read_csv(csv_fn,
        index_col=0,
        usecols=[
            'Flow.ID',
            'Source.IP',
            'Destination.IP',
            'Timestamp',
            'Flow.Duration',
            'Flow.Bytes.s',
            'L7Protocol',
            'ProtocolName'
        ])
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d/%m/%Y%H:%M:%S')

    print('File loaded.')

    return df

# Write output JSON file
def write_json(output_fn, json_data):
    print(f'Writing: {output_fn}')

    with open(output_fn, 'w') as graph_json:
        json.dump(json_data, graph_json)

    print('File written.')

# Print statistics for the network dataset:
def print_stats(df):
    print(f'Number of flows: {df.shape[0]}')
    print(f"First start time : {df['Timestamp'].min()}")
    print(f"Last start time: {df['Timestamp'].max()}")
    print(f"Flow duration [us]: min {df['Flow.Duration'].min()} " \
        f"max {df['Flow.Duration'].max()} " \
        f"mean {df['Flow.Duration'].mean():.2f}")
    print(f"Unique IPs: " \
        f"{len(pd.unique(pd.concat([df['Source.IP'], df['Destination.IP']])))}")

# Filter network flows active at timestamp, and randomly sample up to n flows
def filt_network_flows(df, ts, n=0):
    print("Filtering network flows...")

    df = df[df['Timestamp'] <= ts]
    df = df[df['Timestamp'] +
        pd.to_timedelta(df['Flow.Duration'], unit='us') <= ts]
    if (n > 0) and (n < df.shape[0]):
        print(f"Randomly sampling {n} flows out of {df.shape[0]}")
        df = df.sample(n)

    print("Filtering done.")

    return df

# Create a network graph data structure for all data flows active at ts
def gen_network_flow_graph(df):
    print('Generating Network Flow Graph...')
    nodes_lst = pd.concat([df['Source.IP'], df['Destination.IP']]).unique().tolist()
    edges_src = df['Source.IP'].tolist()
    edges_dest = df['Destination.IP'].tolist()
    edges_fbytes = df['Flow.Bytes.s'].tolist()
    edges_l7_code = df['L7Protocol'].tolist()

    if len(edges_src) != len(edges_dest):
        raise ValueError("Mismatching number of Source and Destination IPs")

    min_flow_rate = df['Flow.Bytes.s'].min()
    max_flow_rate = df['Flow.Bytes.s'].max()

    styles = styles_tmpl

    node_meta = dict()
    nodes = []
    for i, node in enumerate(nodes_lst):
        if node not in node_meta:
            node_meta[node] = { 'idx': i, 'cnts': 0 }

        nodes.append({
            'label': node
        })

    edges = []
    for i in range(len(edges_src)):
        node_meta[edges_src[i]]['cnts'] += 1
        node_meta[edges_dest[i]]['cnts'] += 1

        edges.append({
            'source': node_meta[edges_src[i]]['idx'],
            'target': node_meta[edges_dest[i]]['idx'],
            'style': f'edge-{i}',
        })

        styles[f'edge-{i}'] = {
            'width': scale1toN(edges_fbytes[i],
                min_flow_rate, max_flow_rate, 10),
            'color': toRGBStr(ColorHash(edges_l7_code[i]).rgb)
        }

    num_clients = 0
    num_switches = 0
    for k, v in node_meta.items():
        if v['cnts'] < 3:
            nodes[v['idx']]['style'] = 'client'
            num_clients += 1
        else:
            nodes[v['idx']]['style'] = 'switch'
            num_switches += 1

    df_proto = df.drop_duplicates(subset=['L7Protocol'])
    proto_clrs = df_proto['L7Protocol'].apply(lambda x: toRGBStr(ColorHash(x).rgb)).tolist()
    proto_names = df_proto['ProtocolName'].tolist()
    proto_count = []
    for pname in proto_names:
        proto_count.append(df[df['ProtocolName'] == pname].shape[0])
    proto_lgnd = list(zip(proto_clrs, proto_names, proto_count))

    print('Graph generated.')

    return nodes, edges, styles, proto_lgnd, (num_clients, num_switches)

def main(args):
    df = load_csv(args.input_fn)

    print()
    print(f'== {args.input_fn} stats ==')
    print_stats(df)

    # Filter to instantaneous flows at timestamp
    if args.timestamp:
        ts = clamp(df['Timestamp'].min(),
            datetime.strptime(args.timestamp, '%Y-%m-%d %H:%M:%S'),
            df['Timestamp'].max())
    else:
        ts = df['Timestamp'].min()

    df = filt_network_flows(df, ts, args.flows_limit)
    print()
    print(f'== Filtered ts={ts} stats ==')
    print_stats(df)

    # Assemble graph
    nodes, edges, styles, proto_lgnd, num_clsw = gen_network_flow_graph(df)

    # Write file
    print()
    write_json(args.output_fn, {
        'nodes': nodes,
        'edges': edges,
        'styles': styles,
        'proto_lgnd': proto_lgnd,
        'num_clsw': num_clsw
    })

    print()
    print('Processing done.')

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
