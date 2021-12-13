#!/usr/bin/env python3

# File: gen-all-graphs.py
# Author: Vincent Chung <vwchung2@illinois.edu>
# Course: CS519 - Scientific Visualization (Fall 2021)
# Assignment: Course Project

import argparse
import importlib
import json
import os

parser = argparse.ArgumentParser(
    description='Preprocess all preselected network datasets for graph ' \
        'visualization rendering.')
parser.add_argument('-o', '--output-dir', dest='output_dir', type=str,
    default='../visualization/datasets/',
    help='Output directory of the JSON files')
parser.add_argument('-j', '--json-dir-prefix', dest='json_dir_prefix', type=str,
    default='',
    help='Prefix for relative JS path to JSON files')

class PreprocArgs:
    def __init__(self, input_fn, output_fn, timestamp, flows_limit):
        self.input_fn = input_fn
        self.output_fn = output_fn
        self.timestamp = timestamp
        self.flows_limit = flows_limit

def write_json_graphs(timestamps, num_samples, output_dir):
    preproc_data = importlib.import_module("preproc-data")

    for ts in timestamps:
        for ns in num_samples:
            fname_ts = ts.replace('-', '').replace(':', '').replace(' ', '')
            fname = f'nvg_ts{fname_ts}_nf{ns}.json'
            # cmd = f'./preproc-data.py ' \
            #     f'-n {ns} -t \'{ts}\' ' \
            #     f'-o \'../visualization/datasets/{fname}\' ' \
            #     f'\'\''
            # print(cmd)

            print(f'[gen-all-graphs] Processing ts `{ts}` ns `{ns}`...')

            pargs = PreprocArgs(
                '../../data/Dataset-Unicauca-Version2-87Atts.csv',
                os.path.join(output_dir, fname), ts, ns)
            preproc_data.main(pargs)

def write_manifest(timestamps, num_samples, output_dir, json_prefix):
    graphs_manifest = []

    for ts in timestamps:
        ts_entry = {
            'label': ts[:-3],
            'total_flows': 0, # to be filled manually
            'flow_default': 1, # 300
            'flow_sets': []
        }

        for ns in num_samples:
            fname_ts = ts.replace('-', '').replace(':', '').replace(' ', '')
            fname = f'nvg_ts{fname_ts}_nf{ns}.json'
            ns_entry = {
                'num_flows': ns,
                'fname': json_prefix + fname
            }
            ts_entry['flow_sets'].append(ns_entry)

        graphs_manifest.append(ts_entry)

    manifest_fname = os.path.join(output_dir, 'graphs-manifest.json')
    print(f'[gen-all-graphs] Writing graphs manifest file: {manifest_fname}')
    with open(manifest_fname, 'w') \
            as manifest_file:
        json.dump(graphs_manifest, manifest_file)
    print(f'[gen-all-graphs] Graph manifest written.')

def main(args):
    timestamps = [
        '2017-04-26 09:00:00',
        '2017-04-26 18:00:00',
        '2017-04-27 12:00:00',
        '2017-04-28 22:00:00',

        '2017-05-09 09:00:00',
        '2017-05-09 18:00:00',
    ]
    num_samples = [100, 300, 4000, 10000]

    write_json_graphs(timestamps, num_samples, args.output_dir)
    write_manifest(timestamps, num_samples,
        args.output_dir, args.json_dir_prefix)

if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
