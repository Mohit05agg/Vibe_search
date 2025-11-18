#!/bin/bash
# Script to check and configure PostgreSQL for remote connections

echo "Checking PostgreSQL status..."
sudo service postgresql status

echo ""
echo "Checking if PostgreSQL is listening on port 5432..."
sudo netstat -tlnp | grep 5432 || ss -tlnp | grep 5432

echo ""
echo "To allow connections from Windows, edit /etc/postgresql/18/main/postgresql.conf:"
echo "  listen_addresses = 'localhost'"
echo ""
echo "And edit /etc/postgresql/18/main/pg_hba.conf to add:"
echo "  host    all             all             127.0.0.1/32            md5"
echo "  host    all             all             ::1/128                 md5"

