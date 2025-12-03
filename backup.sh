#!/bin/bash

# 変更をステージング
git add .

# コミット（変更がなければスキップ）
git commit -m "auto backup"

# main に push（初回 push なら -u を付ける）
git push -u origin main

# ZIP バックアップ作成
python3 backup_zip.py

echo "Backup complete!"
