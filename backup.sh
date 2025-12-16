#!/bin/bash
git add .

if ! git diff-index --quiet HEAD --; then
    git commit -m "auto backup $(git branch --show-current)"
fi

# 現在のブランチ名を取得して push
CURRENT_BRANCH=$(git branch --show-current)
git push -u origin "$CURRENT_BRANCH"

python3 backup_zip.py
echo "Backup complete!"
