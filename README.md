# Byte Statistics Analyzer

The **Byte Statistics Analyzer** is a versatile Python tool that provides an in-depth byte-level analysis of files. It not only calculates basic statistics such as byte frequencies, mean, median, and standard deviation, but also dives deeper with advanced metrics like skewness, kurtosis, entropy, rate-of-change, run length, and common multi-byte patterns. This comprehensive analysis makes it invaluable for detailed data inspection.

Developed as part of a broader suite of utilities in this repository, this tool complements other data analysis and processing tools, forming a robust multi-tool environment.

## Features

- **Byte Frequency Analysis:** Computes the count for each byte value (0–255) found in a file.
- **Common & Uncommon Bytes:** Identifies the top three most frequent bytes (displayed in hexadecimal) and the three least frequent non-zero bytes.
- **Comprehensive Statistics:** Calculates mean, median, standard deviation, skewness, kurtosis, and entropy of byte values.
- **Rate-of-Change & Run Analysis:** Evaluates differences between consecutive bytes and analyzes byte runs (max and average lengths) to discover patterns.
- **Pattern Detection:** Detects frequent 2-byte and 4-byte sequences along with their respective counts.
- **Dual Interface:** Offers both command-line options and an intuitive GUI for selecting files or directories.
- **CSV Export Capability:** Optionally exports the analysis results to a CSV file (`byte_stats.csv`) for easy sharing and further processing.

## Requirements

- Python 3.x
- [NumPy](https://numpy.org)
- [Pandas](https://pandas.pydata.org)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)

Install the required packages using:

```
pip install -r requirements.txt
```

## Usage

Run the analyzer from the command line as shown below:

```
python byte-stats.py -f path/to/file1 path/to/file2 --generate-csv
```

### Command-Line Options

- **`-f`, `--files`**: Specify one or more file paths for analysis.  
  If omitted, the tool will launch a GUI file picker.
- **`-d`, `--dirs`**: Specify one or more directory paths (non-recursively) to analyze.  
  If omitted, a GUI directory picker will be launched.
- **`--generate-csv`**: When provided, the tool saves the analysis results to `byte_stats.csv`.

## How It Works

1. **File Reading & Conversion:** Files are opened in binary mode and their contents are converted into a NumPy array.
2. **Data Analysis:** The tool computes an extensive set of statistics, including byte frequency, rate-of-change, run lengths, entropy, and common multi-byte patterns.
3. **Output Generation:** The computed statistics are printed to the console, and if requested, exported to a CSV file.

## Example Scenario

When executed without any command-line arguments:
- The tool automatically opens a GUI file (or directory) picker to let you select files.
- After analysis, detailed byte statistics are displayed in the console.
- If the CSV flag is provided, the results are also saved to `byte_stats.csv`.

## License

This project is open source and distributed under the MIT License. You are free to use, modify, and distribute this tool as part of our growing collection of utilities.

Happy analyzing!
