# Course Project: Network Flow Visualization

CS519 - Scientific Visualization

Vincent Chung <vwchung2@illinois.edu>

## Downloading the network flow dataset

The dataset is publically-available on Kaggle at:
```
https://www.kaggle.com/jsrojas/ip-network-traffic-flows-labeled-with-87-apps
```

## Data preprocessing

The dataset must be preprocessed and converted to a graph JSON representation prior to being loaded by the web application.

```
cd src/preprocess
```

### Individual time + quanity of nodes

```
./preproc-data.py \
    -n 1000 \
    -t '2017-04-26 18:00:00' \
    -o '../visualization/datasets/nvg_ts20170426180000_nf10000.json' \
    '../../data/Dataset-Unicauca-Version2-87Atts.csv'
```

### Generate all times and quanity of nodes

This produces the datasets and manifest shown in the web-based demo.

```
mkdir ../visualization/datasets/
./gen-all-graphs.py -j 'datasets/'
```

## Launching a server

```
cd src/visualization
python3 -m http.server 8080
```

The web page is then viewable at: `http://localhost:8080`.

## Web-hosted demo

Available until mid-January 2022:
```
http://137.184.5.104/ (Credentials: cs519sv / cs519sv)
```
