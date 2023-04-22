# coinflex-history-sync

### What is this?

Uses 
  * coinflex' (coinflex.com) or 
  * opnx' (opnx.com) 
REST API to download and update a local json file with some of the historical data available through the API (trades, mints, redeems, withdrawals, deposits, earned,...)

### State

Works pretty well for a lot of cases, but not all (not all data is covered, but should be easy to extend, just make an issue if you need anything added)

Several API issues are currently worked-around (partially by aborting and informing user), mainly A5, A6 (see the coinflex_issues_*.txt files)

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

#### reset if unsure if data is complete

In case you suspect incomplete data, you can re-download everything by just deleting the coinflex_data.json file and re-running

```
#> rm coinflex_data.json
#> python sync.py
```

Maybe you can copy the file before and after to check if there are differences:

```
#> cp coinflex_data.json coinflex_data_maybeincomplete.json
#> rm coinflex_data.json
#> python sync.py
#> diff coinflex_data.json coinflex_data_maybeincomplete.json
```

and please report problems if you can describe/reproduce them.