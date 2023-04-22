#!/bin/bash

# default for data_file
if [ "$data_file" = "" ]; then
	data_file="opnx_data.json"
fi

# withdrawals
echo '"asset","network","address","quantity","fee","id","status","txId","requestedAt","completedAt"' > withdrawals.csv
cat ${data_file}| jq -r '(.withdrawals.data[] | [.asset, .network, .address, .quantity, .fee, .id, .status, .txId, .requestedAt, .completedAt]) | @csv' | sort -k 10 >> withdrawals.csv

# deposits
echo '"asset","network","address", "quantity", "id", "status", "txId", "crediteddAt"' > deposits.csv
cat ${data_file}| jq -r '(.deposits.data[] | [.asset, .network, .address, .quantity, .id, .status, .txId, .creditedAt]) | @csv' | sort -k8 >> deposits.csv

# trades
echo '"matchId","matchTimestamp","marketCode","matchQuantity","matchPrice","total","orderMatchType","fees","feeInstrumentId","orderId","side","clientOrderId"' > trades.csv
cat ${data_file}| jq -r '(.trades.data[] | [.matchId, .matchTimestamp, .marketCode, .matchQuantity, .matchPrice, .total, .orderMatchType, .fees, .feeInstrumentId, .orderId, .side, .clientOrderId]) | @csv' | sort -k2 >> trades.csv

# mint
echo '"asset","quantity","mintedAt"' > mint.csv
cat ${data_file}| jq -r '(.mint.data[] | [.asset, .quantity, .mintedAt]) | @csv' | sort -k3 >> mint.csv

# redeem 
echo '"asset","quantity","requestedAt","redeemedAt"' > redeem.csv 
cat ${data_file}| jq -r '(.redeem.data[] | [.asset, .quantity, .requestedAt, .redeemedAt]) | @csv' | sort -k4 >> redeem.csv 

# earned
echo '"asset","snapshotQuantity","apr","rate","amount","paidAt"' > earned.csv
cat ${data_file}| jq -r '(.earned.data[] | [.asset, .snapshotQuantity, .apr, .rate, .amount, .paidAt]) | @csv' | sort -k6 >> earned.csv

# wallet
echo '"asset","type","amount","createdAt","accountId","accountName"' > wallet.csv
cat ${data_file}| jq -r '(.wallet.data[] | [.asset, .type, .amount, .createdAt, .accountId, .accountName]) | @csv' | sort -k4 >> wallet.csv

