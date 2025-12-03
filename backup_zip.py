import os
import zipfile
from datetime import datetime
from pathlib import Path

# プロジェクトフォルダ（このスクリプトが置いてある場所）
PROJECT_DIR = Path(__file__).resolve().parent

# ZIP の保存先フォルダ
BACKUP_DIR = PROJECT_DIR / "backups"

# ZIP に含めないフォルダ
EXCLUDE = [
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    "backups"
]

def should_exclude(path):
    return any(ex in str(path) for ex in EXCLUDE)

def zip_project():
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    zip_name = BACKUP_DIR / f"backup_{timestamp}.zip"

    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(PROJECT_DIR):
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
            for file in files:
                file_path = Path(root) / file
                if should_exclude(file_path):
                    continue
                z.write(file_path, file_path.relative_to(PROJECT_DIR))

    print(f"Backup created: {zip_name}")

if __name__ == "__main__":
    zip_project()
