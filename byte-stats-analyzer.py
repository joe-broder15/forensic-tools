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
import tkinter as tk
from tkinter import filedialog
from itertools import groupby          # For computing byte runs
from collections import Counter          # For counting common byte patterns
from scipy.stats import skew, kurtosis   # For distribution characteristics (skewness and kurtosis)

# Import the FilePicker class from utils/file_picker.py
from utils.file_picker import FilePicker

def compute_file_metadata(file: str):
    filename = os.path.basename(file)
    file_type = os.path.splitext(file)[1]
    return filename, file_type

def compute_byte_occurrences(np_bytes: np.ndarray):
    byte_counts = np.bincount(np_bytes, minlength=256)
    total_bytes = byte_counts.sum()
    unique_bytes = np.unique(np_bytes).size
    # Most common: top 3
    most_common_indices = byte_counts.argsort()[-3:][::-1]
    most_common = [f"{hex(byte)} (count: {byte_counts[byte]})" for byte in most_common_indices]
    # Least common: top 3 nonzero
    non_zero_indices = np.where(byte_counts > 0)[0]
    least_common_indices = non_zero_indices[np.argsort(byte_counts[non_zero_indices])[:3]]
    least_common = [f"{hex(byte)} (count: {byte_counts[byte]})" for byte in least_common_indices]
    return byte_counts, total_bytes, unique_bytes, most_common, least_common

def compute_basic_stats(np_bytes: np.ndarray):
    mean_value = hex(int(np.mean(np_bytes)))
    median_value = hex(int(np.median(np_bytes)))
    std_value = hex(int(np.std(np_bytes)))
    return mean_value, median_value, std_value

def compute_rate_of_change(np_bytes: np.ndarray):
    rate_of_change = np.diff(np_bytes)
    if rate_of_change.size > 0:
        mean_rate = hex(int(np.mean(rate_of_change)))
        median_rate = hex(int(np.median(rate_of_change)))
        std_rate = hex(int(np.std(rate_of_change)))
    else:
        mean_rate = hex(0)
        median_rate = hex(0)
        std_rate = hex(0)
    return mean_rate, median_rate, std_rate

def compute_entropy(byte_counts: np.ndarray, total_bytes: int):
    if total_bytes > 0:
        probabilities = byte_counts / total_bytes
        non_zero_probs = probabilities[probabilities > 0]
        entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))
    else:
        entropy = 0
    return entropy

def compute_runs(np_bytes: np.ndarray):
    if np_bytes.size == 0:
        return 0, 0
    # Compute indices where value changes
    changes = np.diff(np_bytes) != 0
    run_ends = np.where(changes)[0] + 1
    # Include start and end indices
    indices = np.concatenate(([0], run_ends, [np_bytes.size]))
    run_lengths = np.diff(indices)
    max_run = run_lengths.max()
    avg_run = run_lengths.mean()
    return int(max_run), float(avg_run)

def compute_patterns(file_bytes: bytes):
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    # 2-byte patterns
    if arr.size >= 2:
        patterns2 = arr[:-1].astype(np.uint16) * 256 + arr[1:].astype(np.uint16)
        uniques2, counts2 = np.unique(patterns2, return_counts=True);
        # Sort indices by descending count
        indices2 = np.argsort(-counts2)[:3]
        common_2byte_patterns = [f"0x{uniques2[i]:04x} (count: {counts2[i]})" for i in indices2]
    else:
        common_2byte_patterns = []

    # 4-byte patterns
    if arr.size >= 4:
        a = arr[:-3].astype(np.uint32) << 24
        b = arr[1:-2].astype(np.uint32) << 16
        c = arr[2:-1].astype(np.uint32) << 8
        d = arr[3:].astype(np.uint32)
        patterns4 = a + b + c + d
        uniques4, counts4 = np.unique(patterns4, return_counts=True)
        indices4 = np.argsort(-counts4)[:3]
        common_4byte_patterns = [f"0x{uniques4[i]:08x} (count: {counts4[i]})" for i in indices4]
    else:
        common_4byte_patterns = []

    return common_2byte_patterns, common_4byte_patterns

def compute_distribution(np_bytes: np.ndarray):
    skewness_value = skew(np_bytes)
    kurtosis_value = kurtosis(np_bytes)
    return skewness_value, kurtosis_value

def compute_autocorrelation(np_bytes: np.ndarray, max_lag: int = 10):
    autocorrs = []
    for lag in range(1, max_lag + 1):
        if len(np_bytes) <= lag:
            autocorrs.append(None)
        else:
            a = np_bytes[:-lag]
            b = np_bytes[lag:]
            if np.std(a) == 0 or np.std(b) == 0:
                autocorrs.append(0)
            else:
                corr = np.corrcoef(a, b)[0, 1]
                autocorrs.append(corr)
    return autocorrs

def compute_even_odd_distribution(np_bytes: np.ndarray):
    even_count = np.sum((np_bytes % 2) == 0)
    odd_count = np.sum((np_bytes % 2) == 1)
    ratio = even_count / odd_count if odd_count != 0 else None
    return {"even": int(even_count), "odd": int(odd_count), "even_to_odd_ratio": ratio}

def compute_ngram_entropy(file_bytes: bytes, n: int):
    if len(file_bytes) < n:
        return 0
    arr = np.frombuffer(file_bytes, dtype=np.uint8)
    shape = (arr.size - n + 1, n)
    strides = (arr.strides[0], arr.strides[0])
    ngrams = np.lib.stride_tricks.as_strided(arr, shape=shape, strides=strides)
    unique, counts = np.unique(ngrams, axis=0, return_counts=True)
    probs = counts / np.sum(counts)
    return -np.sum(probs * np.log2(probs))

def analyze_bytes(file: str) -> dict:
    """Analyze a single file for byte statistics and return a dictionary with the results."""
    # Read file as bytes
    with open(file, "rb") as f:
        file_bytes = f.read()

    # Convert to numpy array
    np_bytes = np.frombuffer(file_bytes, dtype=np.uint8)

    # Compute metadata
    filename, file_type = compute_file_metadata(file)

    # Compute occurrence statistics
    byte_counts, total_bytes, unique_bytes, most_common, least_common = compute_byte_occurrences(np_bytes)

    # Compute basic stats
    mean_value, median_value, std_value = compute_basic_stats(np_bytes)

    # Compute rate-of-change stats
    mean_rate, median_rate, std_rate = compute_rate_of_change(np_bytes)

    # Compute entropy
    entropy_value = compute_entropy(byte_counts, total_bytes)

    # Compute runs
    max_run, avg_run = compute_runs(np_bytes)

    # Compute byte patterns
    common_2byte_patterns, common_4byte_patterns = compute_patterns(file_bytes)

    # Compute distribution characteristics
    skewness_value, kurtosis_value = compute_distribution(np_bytes)

    # Compute additional statistical features
    autocorrs = compute_autocorrelation(np_bytes)
    even_odd_distribution = compute_even_odd_distribution(np_bytes)
    ngram_entropy = compute_ngram_entropy(file_bytes, 3)

    stats = {
        # File Metadata
        'filename': filename,
        'file_type': file_type,
        
        # Byte Occurrence Statistics
        'total_bytes': total_bytes,
        'unique_bytes': unique_bytes,
        'most_common_bytes': most_common,
        'least_common_bytes': least_common,
        
        # Basic Byte Value Statistics
        'mean_byte_value': mean_value,
        'median_byte_value': median_value,
        'std_dev_byte_value': std_value,
        
        # Rate-of-Change Metrics
        'mean_rate_of_change': mean_rate,
        'median_rate_of_change': median_rate,
        'std_dev_rate_of_change': std_rate,
        
        # Distribution and Pattern Analyses
        'entropy': entropy_value,
        'max_run_length': max_run,
        'avg_run_length': avg_run,
        'common_2byte_patterns': common_2byte_patterns,
        'common_4byte_patterns': common_4byte_patterns,
        
        # Distribution Characteristics
        'skewness': skewness_value,
        'kurtosis': kurtosis_value,
        
        # Additional Statistical Features
        'autocorrelation': autocorrs,
        'even_odd_distribution': even_odd_distribution,
        'ngram_entropy': ngram_entropy
    }

    return stats

def print_stats(stats_list: list):
    """Pretty print the list of statistics dictionaries in a command-line friendly format."""
    for i, stats in enumerate(stats_list, start=1):
        print(f"FILE #{i}: {stats['filename']}")
        print(f"  File Type: {stats['file_type']}")
        print(f"  Byte Occurrence Statistics:")
        print(f"    Total Bytes: {stats['total_bytes']}")
        print(f"    Unique Bytes: {stats['unique_bytes']}")
        most_common = ', '.join(stats['most_common_bytes']) if stats['most_common_bytes'] else 'N/A'
        least_common = ', '.join(stats['least_common_bytes']) if stats['least_common_bytes'] else 'N/A'
        print(f"    Most Common Bytes: {most_common}")
        print(f"    Least Common Bytes: {least_common}")

        print(f"  Basic Byte Value Statistics:")
        print(f"    Mean Value: {stats['mean_byte_value']}")
        print(f"    Median Value: {stats['median_byte_value']}")
        print(f"    Std Dev: {stats['std_dev_byte_value']}")

        print(f"  Rate-of-Change Metrics:")
        print(f"    Mean Rate: {stats['mean_rate_of_change']}")
        print(f"    Median Rate: {stats['median_rate_of_change']}")
        print(f"    Std Dev Rate: {stats['std_dev_rate_of_change']}")

        print(f"  Additional Statistics:")
        print(f"    Entropy: {stats['entropy']}")
        print(f"    Max Run Length: {stats['max_run_length']}")
        print(f"    Avg Run Length: {stats['avg_run_length']}")
        print(f"    Skewness: {stats['skewness']}")
        print(f"    Kurtosis: {stats['kurtosis']}")

        print(f"  Common Byte Patterns:")
        pattern2 = ', '.join(stats['common_2byte_patterns']) if stats['common_2byte_patterns'] else 'N/A'
        pattern4 = ', '.join(stats['common_4byte_patterns']) if stats['common_4byte_patterns'] else 'N/A'
        print(f"    2-byte Patterns: {pattern2}")
        print(f"    4-byte Patterns: {pattern4}")
        
        print(f"  Additional Statistical Features:")
        # Format autocorrelation values
        autocorr_values = [f"{val:.4f}" for val in stats['autocorrelation']]
        print(f"    Autocorrelation (lags 1-10): {autocorr_values}")
        
        # Format even/odd distribution
        even_odd = stats['even_odd_distribution']
        ratio = even_odd['even_to_odd_ratio']
        ratio_str = f"{ratio:.4f}" if ratio is not None else "N/A"
        print(f"    Even/Odd Distribution: {even_odd['even']} even bytes, {even_odd['odd']} odd bytes (ratio: {ratio_str})")
        
        # Format n-gram entropy
        print(f"    N-gram Entropy (3-byte): {stats['ngram_entropy']:.4f}")
        print("\n")

def main():
    parser = argparse.ArgumentParser(description='Analyze files for byte statistics.')
    parser.add_argument("-f", "--files", nargs="*", default=[], help="File(s) to analyze.")
    parser.add_argument("-d", "--dirs", nargs="*", default=[], help="Directory(ies) to analyze (non-recursive).")
    parser.add_argument("--generate-csv", action="store_true", help="Generate a CSV file with the analysis results.")
    args = parser.parse_args()

    # Use the FilePicker class to get input files
    files = FilePicker.get_input_files(args)
    if not files:
        print("No valid files provided. Exiting...")
        return

    # Analyze each file and collect their statistics as dictionaries
    stats_list = []
    total_files = len(files)
    for i, file in enumerate(files, 1):
        try:
            stats = analyze_bytes(file)
            stats_list.append(stats)
            print(f"FILE {i}/{total_files} finished processing. [{file}]")
        except Exception as e:
            print(f"Error analyzing {file}: {e}")

    if not stats_list:
        print("No data to analyze. Exiting...")
        return

    # Pretty print stats
    print_stats(stats_list)

    if args.generate_csv:
        # If CSV generation is desired, convert to CSV format
        # Note: Since we are not using pandas, we will manually generate a CSV
        import csv
        # Get header from the first dictionary
        header = list(stats_list[0].keys())
        with open("byte_stats.csv", "w", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for stats in stats_list:
                writer.writerow(stats)
        print("Statistics saved to 'byte_stats.csv'.")

if __name__ == "__main__":
    main()
