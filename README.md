# 📅 Image Date Corrector

**Prototype for EXIF date correction**  
_Batch-process JPG photos with incorrect timestamps_

## ⛈️ The problem

When transferring old photos to modern galleries (like Apple Photos), incorrect EXIF dates can cause wrong organization.
This tool helps reset creation dates for JPG files.

## ⚙️ Current Features

### Core Functionality

- 🔍 **JPG scanning** - Finds `.jpg` and `.jpeg` files in folder
- 📅 **Date threshold check** - Flags files newer than specified date
- ✏️ **EXIF overwrite** - Updates `DateTime`, `DateTimeOriginal`, `DateTimeDigitized`

### Known limits

- 🖼 **Formats** - Only JPG/JPEG fully supported
- ↩️ **No undo** - Changes are permanent (backup recommended)
- 📝 **Manual batch** - Edit `main.py` to process different folders

## 🧑💻 Basic workflow:

```ascii
1. [Your Photos]
   └── 📂 Folder
       ├── 📷 photo1.jpg (Date: 2025)
       └── 📷 photo2.jpg (Date: 2015)

2. [Script Runs] → Finds 2025-dated photo

3. [EXIF Update] → photo1.jpg becomes 2015  
```

## 🛠 How to use

### Installation

1. Install [Python](https://www.python.org/) (≥3.12)

2. Clone repository

3. Install requirements:

```bash
pip install -r requirements.txt
```

### Usage

1. Edit `main.py` with your path/dates:

```python
def main():
    DIR_PATH = "/path/to/your/photos"  # 🔑 Change this
    MAX_DATE = datetime(2025, 1, 1)  # 📅 Photos NEWER than this will be changed
    CHANGE_DATE = datetime(2025, 1, 1)  # 🎯 New date to set
```

2. Run script:

```bash
python main.py
```

## ⚠️ Important Notes

- ❗ **Always backup photos first**
- ❗ Test on copies before processing originals
- ❗ Only works with EXIF-aware apps (Finder dates unchanged)

## 🤝 Contributing

If you want to contribute to a project and make it better, your help is very welcome! Fork it and create merge request!

### 🔮 Ideas

- ⚙️ CLI arguments — Configure paths/dates via command line
- 🧪 `--dry-run` flag — Test without modifying files
- 📋 Logging — Preserve change history for potential undo
- 🖼 PNG/HEIC support

---

🔨 Made with care - Not yet production-grade but functional for JPGs.