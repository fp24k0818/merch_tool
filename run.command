#!/bin/zsh

cd "$(dirname "$0")"

echo "物販チェックツールを起動します..."
python main.py

echo ""
echo "Enterキーで終了します"
read
