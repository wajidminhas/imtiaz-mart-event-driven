#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE userdb;
    CREATE DATABASE productdb;
    CREATE DATABASE orderdb;
    CREATE DATABASE inventorydb;
    CREATE DATABASE paymentdb;
EOSQL

echo "Multiple databases created successfully!"