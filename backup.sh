#!/bin/bash
git add .
git commit -m "auto backup"
git push origin master
python3 backup_zip.py
echo "Backup complete!"
