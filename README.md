# coinflex-history-sync

### What is this?

Uses coinflex' (coinflex.com) REST API to download and update a local json file with all the historical data (trades, mints, redeems, withdrawals, deposits,...)

### State

Not in good shape yet. 

This is currently a work-in-progress hackjob that just about "works for me". In case of demand I will improve.

### Usage

#### getting started first time

```
#> cp config_example.py config.py
#> $EDITOR config.py
#> python sync.py
```

This should create a local file `coinflex_data.json` containing all the data that was pulled from the API.

#### subsequent updates

Running sync.py again should only fetch new data and append it to `coinflex_data.json`

```
#> python sync.py
```
