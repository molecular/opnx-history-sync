#!/bin/bash

# withdrawals
echo '"asset","network","address","quantity","fee","id","status","txId","requestedAt","completedAt"' > withdrawals.csv
cat coinflex_data.json| jq -r '(.withdrawals.data[] | [.asset, .network, .address, .quantity, .fee, .id, .status, .txId, .requestedAt, .completedAt]) | @csv' | sort -k 10 >> withdrawals.csv

# deposits
echo '"asset","network","address", "quantity", "id", "status", "txId", "crediteddAt"' > deposits.csv
cat coinflex_data.json| jq -r '(.deposits.data[] | [.asset, .network, .address, .quantity, .id, .status, .txId, .creditedAt]) | @csv' | sort -k8 >> deposits.csv

# trades
echo '"matchId","matchTimestamp","marketCode","matchQuantity","matchPrice","total","orderMatchType","fees","feeInstrumentId","orderId","side","clientOrderId"' > trades.csv
cat coinflex_data.json| jq -r '(.trades.data[] | [.matchId, .matchTimestamp, .marketCode, .matchQuantity, .matchPrice, .total, .orderMatchType, .fees, .feeInstrumentId, .orderId, .side, .clientOrderId]) | @csv' | sort -k2 >> trades.csv

# mint
echo '"asset","quantity","mintedAt"' > mint.csv
cat coinflex_data.json| jq -r '(.mint.data[] | [.asset, .quantity, .mintedAt]) | @csv' | sort -k3 >> mint.csv

# redeem 
echo '"asset","quantity","requestedAt","redeemedAt"' > redeem.csv 
cat coinflex_data.json| jq -r '(.redeem.data[] | [.asset, .quantity, .requestedAt, .redeemedAt]) | @csv' | sort -k4 >> redeem.csv 

# earned
echo '"asset","snapshotQuantity","apr","rate","amount","paidAt"' > earned.csv
cat coinflex_data.json| jq -r '(.earned.data[] | [.asset, .snapshotQuantity, .apr, .rate, .amount, .paidAt]) | @csv' | sort -k6 >> earned.csv

# wallet
echo '"asset","type","amount","createdAt","accountId","accountName"' > wallet.csv
cat coinflex_data.json| jq -r '(.wallet.data[] | [.asset, .type, .amount, .createdAt, .accountId, .accountName]) | @csv' | sort -k4 >> wallet.csv

