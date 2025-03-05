# Forensic Tools

A collection of Python-based forensic analysis tools designed for detailed file examination and metadata extraction. This repository contains utilities that help with digital forensics, file analysis, and metadata inspection.

## Tools Included

### 1. Byte Statistics Analyzer

A comprehensive tool that provides in-depth byte-level analysis of files, calculating various statistical metrics and identifying patterns.

**Features:**
- Byte frequency analysis and distribution statistics
- Identification of common and uncommon bytes (displayed in hex)
- Statistical measures: mean, median, standard deviation, skewness, kurtosis, and entropy
- Rate-of-change analysis between consecutive bytes
- Run length analysis to discover patterns
- Detection of frequent 2-byte and 4-byte sequences
- CSV export capability for further analysis

### 2. EXIF Analyzer

A specialized tool for extracting and analyzing EXIF metadata from image files, providing detailed information about images and their origins.

**Features:**
- Comprehensive extraction of EXIF metadata from image files
- Detailed display of tag information with proper categorization
- Support for all standard EXIF IFDs (Image File Directories)
- Hierarchical display of nested metadata structures
- Verbose mode for detailed tag information including tag IDs and data types

## Common Features

Both tools share these capabilities:
- Dual interface: command-line options and intuitive GUI
- Batch processing of multiple files
- Directory-based analysis
- Detailed output formatting

## Project Structure

```
forensic-tools/
├── byte-stats-analyzer.py  # Byte-level file analysis tool
├── exif-analyzer.py        # EXIF metadata extraction tool
├── requirements.txt        # Python dependencies
├── utils/                  # Shared utility modules
│   ├── __init__.py
│   └── file_picker.py      # Unified file selection interface
└── LICENSE                 # MIT License
```

## Requirements

```
numpy
pandas
tk
scipy
piexif
```

Install the required packages using:

```
pip install -r requirements.txt
```

## Usage

### Byte Statistics Analyzer

```
python byte-stats-analyzer.py -f path/to/file1 path/to/file2 --generate-csv
```

**Command-Line Options:**
- `-f`, `--files`: Specify one or more file paths for analysis
- `-d`, `--dirs`: Specify one or more directory paths to analyze
- `--generate-csv`: Save analysis results to CSV file

### EXIF Analyzer

```
python exif-analyzer.py -f path/to/image1.jpg path/to/image2.jpg --verbose
```

**Command-Line Options:**
- `-f`, `--files`: Specify one or more image files for analysis
- `-d`, `--dirs`: Specify one or more directory paths containing images
- `-v`, `--verbose`: Display detailed tag information including tag IDs and types

## GUI Mode

If you run either tool without specifying files or directories, a graphical file picker will launch automatically, allowing you to select files or directories interactively.

## Utility Modules

The repository includes a `utils` package with reusable components:
- `file_picker.py`: A unified interface for file selection operations that supports both GUI and command-line modes

## License

This project is open source and distributed under the MIT License. You are free to use, modify, and distribute these tools as needed.

Happy analyzing!
