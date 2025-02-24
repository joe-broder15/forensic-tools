# Byte Statistics Analyzer

The **Byte Statistics Analyzer** is a Python tool that examines files at the byte level, providing detailed statistics and insights on their content. It leverages both command-line arguments and a graphical user interface (GUI) for file or directory selection, ensuring flexible usage in various environments.

## Features

- **Byte Frequency Analysis:** Calculates the count for each byte value (0–255) present in a file.
- **Common & Uncommon Bytes:** Identifies the top three most common bytes (displayed in hexadecimal) and the three least common non-zero bytes.
- **Statistical Measures:** Computes key metrics such as mean, median, and standard deviation for the byte values.
- **Rate-of-Change Analysis:** Evaluates the differences between consecutive bytes to provide insights into data variability.
- **Dual Interface:** Supports both command-line arguments and interactive GUI selectors for file and directory inputs.
- **CSV Export Capability:** Optionally outputs the analysis results into a CSV file (`byte_stats.csv`) for easy data sharing and post-processing.

## Requirements

- Python 3.x
- [NumPy](https://numpy.org)
- [Pandas](https://pandas.pydata.org)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)

Install the necessary packages with:

```
pip install -r requirements.txt
```

## Usage

Run the analyzer via the command line:

```
python byte-stats.py -f path/to/file1 path/to/file2 --generate-csv
```

### Command-Line Options

- **`-f`, `--files`**: Specify one or more file paths to analyze.  
  If omitted, the script will launch a GUI file picker.
- **`-d`, `--dirs`**: Specify one or more directory paths.  
  The script will analyze files (non-recursively) found within these directories.  
  If omitted, a GUI directory picker will be launched.
- **`--generate-csv`**: When provided, the analysis results are saved to a CSV file named `byte_stats.csv`.

## How It Works

1. **File Reading:** Files are opened in binary mode and their contents read into a NumPy array.
2. **Analysis:** Byte-level statistics are computed, including frequency counts, common/uncommon bytes, and rate-of-change metrics.
3. **Output:** Results are displayed in the console and can optionally be exported to a CSV file.

## Example Scenario

If you run the script without any command-line arguments:
- The tool will automatically prompt you with a GUI file picker to select the files to analyze.
- After analysis, the byte statistics are printed to the console.
- Optionally, if you specify the CSV flag, the results will be saved as `byte_stats.csv`.

## License

This project is open source and distributed under the MIT License. You are free to use, modify, and distribute this tool as needed.

Happy analyzing!
