"""
Byte Statistics Analyzer

This script analyzes one or more files for various byte-level statistics.
It provides both command-line and graphical (GUI) interfaces for file or directory selection.

Features:
- Parses files to compute frequency counts and statistical measures.
- Computes common and uncommon bytes (displayed in hex).
- Computes rate-of-change statistics for consecutive bytes.
- Allows file selection via command-line flags or GUI.
- Saves results to a CSV file.
"""
import os 
import argparse  # using argparse for command-line arguments
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from itertools import groupby          # For computing byte runs
from collections import Counter          # For counting common byte patterns
from scipy.stats import skew, kurtosis   # For distribution characteristics (skewness and kurtosis)

def analyze_file(file: str) -> pd.DataFrame:
    """
    Analyze the given file for byte statistics and return a DataFrame containing the results.
    
    Parameters:
        file (str): Path to the file to analyze.
        
    Returns:
        pd.DataFrame: Single-row DataFrame with statistics for the file.
    """
    # Read file bytes from disk
    with open(file, "rb") as f:
        file_bytes = f.read()

    # Convert file content to a numpy array of uint8
    np_bytes = np.frombuffer(file_bytes, dtype=np.uint8)

    # Calculate byte frequency ensuring count for each byte value (0-255)
    byte_counts = np.bincount(np_bytes, minlength=256)

    # Determine the top 3 most common bytes (as hex strings)
    most_common_indices = byte_counts.argsort()[-3:][::-1]
    most_common = [f"{hex(byte)} (count: {byte_counts[byte]})" for byte in most_common_indices]

    # Determine the top 3 least common bytes (excluding those with zero count)
    non_zero_indices = np.where(byte_counts > 0)[0]
    least_common_indices = non_zero_indices[np.argsort(byte_counts[non_zero_indices])[:3]]
    least_common = [f"{hex(byte)} (count: {byte_counts[byte]})" for byte in least_common_indices]

    # Calculate various statistics
    total_bytes = byte_counts.sum()
    nonzero_bytes = (np_bytes > 0).sum()
    unique_bytes = np.unique(np_bytes).size
    mean_value = hex(int(np.mean(np_bytes)))
    median_value = hex(int(np.median(np_bytes)))
    std_value = hex(int(np.std(np_bytes)))
    
    # Calculate rate-of-change statistics (differences between consecutive bytes)
    rate_of_change = np.diff(np_bytes)
    if rate_of_change.size > 0:
        mean_rate_of_change = hex(int(np.mean(rate_of_change)))
        median_rate_of_change = hex(int(np.median(rate_of_change)))
        std_rate_of_change = hex(int(np.std(rate_of_change)))
    else:
        mean_rate_of_change = hex(0)
        median_rate_of_change = hex(0)
        std_rate_of_change = hex(0)

    # Calculate entropy of the byte distribution
    probabilities = byte_counts / total_bytes if total_bytes > 0 else np.zeros_like(byte_counts, dtype=float)
    non_zero_probs = probabilities[probabilities > 0]
    entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))

    # Analyze byte runs: maximum run length and average run length
    runs = [len(list(g)) for _, g in groupby(np_bytes)]
    max_run_length = max(runs) if runs else 0
    avg_run_length = sum(runs) / len(runs) if runs else 0

    # Analyze common byte patterns for 2-byte sequences
    if len(file_bytes) >= 2:
        patterns2 = [file_bytes[i:i+2] for i in range(len(file_bytes) - 1)]
        counter2 = Counter(pattern.hex() for pattern in patterns2)
        common_2byte_patterns = [f"{pat} (count: {cnt})" for pat, cnt in counter2.most_common(3)]
    else:
        common_2byte_patterns = []

    # Analyze common byte patterns for 4-byte sequences
    if len(file_bytes) >= 4:
        patterns4 = [file_bytes[i:i+4] for i in range(len(file_bytes) - 3)]
        counter4 = Counter(pattern.hex() for pattern in patterns4)
        common_4byte_patterns = [f"{pat} (count: {cnt})" for pat, cnt in counter4.most_common(3)]
    else:
        common_4byte_patterns = []

    # Calculate distribution characteristics: skewness and kurtosis of byte values
    skewness_value = skew(np_bytes)
    kurtosis_value = kurtosis(np_bytes)

    # Extract file information
    file_type = os.path.splitext(file)[1]
    filename = os.path.basename(file)

    # Compile all statistics into a dictionary with grouped and logically ordered data
    stats = {
        # File Metadata
        'filename': filename,
        'file_type': file_type,
        
        # Byte Occurrence Statistics
        'total_bytes': total_bytes,
        'nonzero_bytes': nonzero_bytes,
        'unique_bytes': unique_bytes,
        'most_common_bytes': most_common,
        'least_common_bytes': least_common,
        
        # Basic Byte Value Statistics
        'mean_byte_value': mean_value,
        'median_byte_value': median_value,
        'std_dev_byte_value': std_value,
        'skewness': skewness_value,
        'kurtosis': kurtosis_value,
        
        # Rate-of-Change Metrics
        'mean_rate_of_change': mean_rate_of_change,
        'median_rate_of_change': median_rate_of_change,
        'std_dev_rate_of_change': std_rate_of_change,
        
        # Distribution and Pattern Analyses
        'entropy': entropy,
        'max_run_length': max_run_length,
        'avg_run_length': avg_run_length,
        'common_2byte_patterns': common_2byte_patterns,
        'common_4byte_patterns': common_4byte_patterns
    }

    # Define the column order for the output DataFrame following the grouped structure
    columns = [
        'filename', 'file_type',
        'total_bytes', 'nonzero_bytes', 'unique_bytes', 'most_common_bytes', 'least_common_bytes',
        'mean_byte_value', 'median_byte_value', 'std_dev_byte_value', 'skewness', 'kurtosis',
        'mean_rate_of_change', 'median_rate_of_change', 'std_dev_rate_of_change',
        'entropy', 'max_run_length', 'avg_run_length', 'common_2byte_patterns', 'common_4byte_patterns'
    ]
    
    return pd.DataFrame([stats], columns=columns)

def analyze_files(files: list[str]) -> pd.DataFrame:
    """
    Analyze multiple files and combine their statistics into a single DataFrame.
    
    Parameters:
        files (list[str]): List of file paths to analyze.
        
    Returns:
        pd.DataFrame: DataFrame containing statistics for each file.
    """
    # Use list comprehension to collect individual DataFrames
    dataframes = [analyze_file(file) for file in files if os.path.isfile(file)]
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no valid files found

def print_file_stats(df: pd.DataFrame):
    """
    Print the statistics for each analyzed file contained in the DataFrame.
    
    Parameters:
        df (pd.DataFrame): DataFrame with byte statistics.
    """
    for i, row in enumerate(df.itertuples(index=False), start=1):
        print(f"FILE #{i}: {row.filename}")
        # Iterate through all fields in the row
        for field, value in row._asdict().items():
            if isinstance(value, (list, np.ndarray)):
                # Convert each element of the array to a string and join them with commas
                print(f"    {field}: {', '.join(str(item) for item in value)}")
            else:
                print(f"    {field}: {value}")
        print()

def pick_files_gui() -> list[str]:
    """
    Launch a GUI file picker for the user to select files.
    
    Returns:
        list[str]: List of selected file paths.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    files = list(filedialog.askopenfilenames(title="Select files to analyze"))
    root.destroy()  # Close the Tkinter instance
    return files

def pick_directory_gui() -> list[str]:
    """
    Launch a GUI directory picker and list files from the selected directory (non-recursively).
    
    Returns:
        list[str]: List of file paths from the selected directory.
    """
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title="Select directory to analyze")
    root.destroy()

    if not directory:
        return []
    files = [os.path.join(directory, f) for f in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, f))]
    return files

def get_input_files(args: argparse.Namespace) -> list[str]:
    """
    Process command-line arguments to determine which files to analyze.
    
    Behavior:
      - If the file flag (-f/--files) is provided with arguments, validate each file.
      - If the file flag is provided with no arguments, launch the file picker GUI.
      - If the directory flag (-d/--dirs) is provided with arguments, list files from each directory (non-recursive).
      - If the directory flag is provided with no arguments, launch the directory picker GUI.
      - If neither flag is provided, default to the file picker GUI.
    
    Parameters:
        args (argparse.Namespace): Parsed command-line arguments.
    
    Returns:
        list[str]: List of file paths to analyze.
    """
    import sys
    files = []
    
    # Process file flag (-f/--files)
    if '-f' in sys.argv or '--files' in sys.argv:
        if args.files:
            for f in args.files:
                if os.path.isfile(f):
                    files.append(f)
                    print(f"File '{f}' provided.")
                else:
                    print(f"Error: '{f}' is not a valid file.")
        else:
            print("File flag set with no arguments; launching file picker GUI...")
            gui_files = pick_files_gui()
            if not gui_files:
                print("No files selected.")
            files.extend(gui_files)
    
    # Process directory flag (-d/--dirs)
    if '-d' in sys.argv or '--dirs' in sys.argv:
        if args.dirs:
            for d in args.dirs:
                if os.path.isdir(d):
                    dir_files = [os.path.join(d, f) for f in os.listdir(d)
                                 if os.path.isfile(os.path.join(d, f))]
                    if dir_files:
                        print(f"Directory '{d}' provided with {len(dir_files)} files.")
                    else:
                        print(f"Directory '{d}' does not contain any files.")
                    files.extend(dir_files)
                else:
                    print(f"Error: '{d}' is not a valid directory.")
        else:
            print("Directory flag set with no arguments; launching directory picker GUI...")
            gui_dir_files = pick_directory_gui()
            if not gui_dir_files:
                print("No files found in selected directory.")
            files.extend(gui_dir_files)
    
    # Default to file picker GUI if no flags are provided
    if not any(flag in sys.argv for flag in ('-f', '--files', '-d', '--dirs')):
        print("No command-line arguments provided; using file picker GUI...")
        gui_files = pick_files_gui()
        if not gui_files:
            print("No files selected.")
        files.extend(gui_files)
    
    return files

def main():
    """
    Main function for the Byte Statistics Analyzer.
    
    It parses command-line arguments, retrieves the input files using the appropriate
    methods (command-line or GUI), analyzes the files, prints the resulting statistics,
    and saves them to a CSV file if requested.
    """
    parser = argparse.ArgumentParser(description='Analyze files for byte statistics.')
    parser.add_argument("-f", "--files", nargs="*", default=[], help="File(s) to analyze.")
    parser.add_argument("-d", "--dirs", nargs="*", default=[], help="Directory(ies) to analyze (non-recursive).")
    parser.add_argument("--generate-csv", action="store_true", help="Generate a CSV file with the analysis results. Defaults to off.")
    args = parser.parse_args()

    files = get_input_files(args)
    if not files:
        print("No valid files provided. Exiting...")
        return

    df = analyze_files(files)
    if df.empty:
        print("No data to analyze. Exiting...")
        return

    print_file_stats(df)

    if args.generate_csv:
        df.to_csv("byte_stats.csv", index=False)
        print("Statistics saved to 'byte_stats.csv'.")

if __name__ == "__main__":
    main()
