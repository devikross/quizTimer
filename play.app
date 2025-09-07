#! /bin/bash

echo 'INICIANDO'
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
~/.mi_entorno/bin/python main.py
echo "Press any key to continue..."
read -n1
