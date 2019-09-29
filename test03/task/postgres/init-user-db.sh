#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" << EOSQL
    create database $WP_DB_NAME;
    create user $WP_DB_USER with password '$WP_DB_PASS';
    grant all privileges on database $WP_DB_NAME to $WP_DB_USER;	
EOSQL
