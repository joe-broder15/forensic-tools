"""
EXIF Analyzer

This script analyzes one or more image files for EXIF metadata.
It provides both command-line and graphical (GUI) interfaces for file or directory selection.

Features:
- Parses image files to extract EXIF metadata
- Allows file selection via command-line flags or GUI
"""
import os
import argparse
import struct
import piexif
from utils.file_picker import FilePicker


def print_tag_value(ifd_name, tag, value, indent_level=0, verbose=False):
    """
    Print a tag and its value with proper indentation.
    
    Parameters:
        ifd_name (str): Name of the IFD containing the tag
        tag (int): Tag identifier
        value: Tag value
        indent_level (int): Current indentation level
        verbose (bool): Whether to display detailed tag information
    """
    indent = "    " * indent_level
    tag_info = piexif.TAGS.get(ifd_name, {}).get(tag, {})
    tag_name = tag_info.get("name", f"Unknown tag: 0x{tag:04X}")
    
    # Get tag type information for verbose mode
    tag_type = tag_info.get("type", "Unknown") if verbose else None
    
    # Format tag ID as hexadecimal
    tag_hex = f"0x{tag:04X}"
    
    # Handle different value types
    if isinstance(value, bytes):
        try:
            # Try to decode as ASCII if possible
            decoded_value = value.decode('ascii', errors='replace')
            if verbose:
                print(f"{indent}{tag_name}: {decoded_value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: bytes]")
            else:
                print(f"{indent}{tag_name}: {decoded_value}")
        except:
            if verbose:
                print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: bytes]")
            else:
                print(f"{indent}{tag_name}: {value}")
    elif isinstance(value, tuple) and len(value) == 2:
        # Handle rational numbers
        if value[1] != 0:
            if verbose:
                print(f"{indent}{tag_name}: {value[0]}/{value[1]} ({value[0]/value[1]:.4f}) [Tag ID: {tag_hex}, Type: {tag_type}, Format: rational]")
            else:
                print(f"{indent}{tag_name}: {value[0]}/{value[1]} ({value[0]/value[1]:.4f})")
        else:
            if verbose:
                print(f"{indent}{tag_name}: {value[0]}/0 [Tag ID: {tag_hex}, Type: {tag_type}, Format: rational]")
            else:
                print(f"{indent}{tag_name}: {value[0]}/0")
    elif isinstance(value, int):
        if verbose:
            print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: integer]")
        else:
            print(f"{indent}{tag_name}: {value}")
    elif isinstance(value, list) or isinstance(value, tuple):
        if verbose:
            print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: array, Length: {len(value)}]")
        else:
            print(f"{indent}{tag_name}: {value}")
    else:
        if verbose:
            print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: {type(value).__name__}]")
        else:
            print(f"{indent}{tag_name}: {value}")
    
    # Return True if this tag might contain a sub-IFD
    return tag in [34665, 34853, 40965]  # Exif IFD, GPS IFD, Interop IFD


def process_tags(ifd_name, ifd_dict, exif_dict, indent_level=0, verbose=False):
    """
    Process and print all tags in an IFD.
    
    Parameters:
        ifd_name (str): Name of the IFD
        ifd_dict (dict): Dictionary containing tag data
        exif_dict (dict): Full EXIF dictionary for sub-IFD lookup
        indent_level (int): Current indentation level
        verbose (bool): Whether to display detailed tag information
    """
    indent = "    " * indent_level
    print(f"{indent}Tags in {ifd_name}:")
    
    for tag, value in ifd_dict.items():
        is_sub_ifd_pointer = print_tag_value(ifd_name, tag, value, indent_level + 1, verbose)
        
        # Check if this tag points to a sub-IFD
        if is_sub_ifd_pointer:
            # Map tag numbers to their corresponding IFD names in the exif_dict
            sub_ifd_map = {
                34665: "Exif",    # Exif IFD Pointer
                34853: "GPS",     # GPS IFD Pointer
                40965: "Interop"  # Interoperability IFD Pointer
            }
            
            if tag in sub_ifd_map and sub_ifd_map[tag] in exif_dict:
                sub_ifd_name = sub_ifd_map[tag]
                sub_ifd_dict = exif_dict[sub_ifd_name]
                
                if sub_ifd_dict:
                    print(f"{indent}    Sub-IFD: {sub_ifd_name}")
                    process_sub_ifd(sub_ifd_name, sub_ifd_dict, exif_dict, indent_level + 2, verbose)


def process_sub_ifd(ifd_name, ifd_dict, exif_dict, indent_level=0, verbose=False):
    """
    Process a sub-IFD and its tags.
    
    Parameters:
        ifd_name (str): Name of the sub-IFD
        ifd_dict (dict): Dictionary containing sub-IFD data
        exif_dict (dict): Full EXIF dictionary for further sub-IFD lookup
        indent_level (int): Current indentation level
        verbose (bool): Whether to display detailed tag information
    """
    # Display additional sub-IFD information in verbose mode
    if verbose:
        indent = "    " * indent_level
        item_count = len(ifd_dict)
        print(f"{indent}[Sub-IFD Info: {item_count} tags]")
        
        # Count different types of values
        value_types = {}
        for tag, value in ifd_dict.items():
            value_type = type(value).__name__
            value_types[value_type] = value_types.get(value_type, 0) + 1
        
        # Print value type distribution
        if value_types:
            type_info = ", ".join([f"{count} {type_name}s" for type_name, count in value_types.items()])
            print(f"{indent}[Value types: {type_info}]")
    
    # Process tags in this sub-IFD
    process_tags(ifd_name, ifd_dict, exif_dict, indent_level, verbose)


def process_ifd(ifd_name, ifd_dict, exif_dict, indent_level=0, verbose=False):
    """
    Process an IFD and its tags.
    
    Parameters:
        ifd_name (str): Name of the IFD
        ifd_dict (dict): Dictionary containing IFD data
        exif_dict (dict): Full EXIF dictionary for sub-IFD lookup
        indent_level (int): Current indentation level
        verbose (bool): Whether to display detailed tag information
    """
    indent = "    " * indent_level
    print(f"{indent}IFD: {ifd_name}")
    
    # Display additional IFD information in verbose mode
    if verbose:
        item_count = len(ifd_dict)
        print(f"{indent}    [IFD Info: {item_count} tags]")
        
        # Count different types of values
        value_types = {}
        for tag, value in ifd_dict.items():
            value_type = type(value).__name__
            value_types[value_type] = value_types.get(value_type, 0) + 1
        
        # Print value type distribution
        type_info = ", ".join([f"{count} {type_name}s" for type_name, count in value_types.items()])
        print(f"{indent}    [Value types: {type_info}]")
    
    # Process tags in this IFD
    process_tags(ifd_name, ifd_dict, exif_dict, indent_level + 1, verbose)
    
    # Check for thumbnail IFD in Exif IFD
    if ifd_name == "Exif" and "thumbnail" in exif_dict:
        print(f"{indent}    Thumbnail data present")


def process_exif_dict(exif_dict, indent_level=0, verbose=False):
    """
    Process and print all IFDs in the EXIF dictionary.
    
    Parameters:
        exif_dict (dict): Dictionary containing all EXIF data
        indent_level (int): Current indentation level
        verbose (bool): Whether to display detailed tag information
    """
    # Dynamically iterate over all present IFDs in the EXIF dictionary
    for ifd_name, ifd_data in exif_dict.items():
        # Skip the thumbnail data which is not an IFD
        if ifd_name == "thumbnail":
            if ifd_data:
                indent = "    " * indent_level
                print(f"{indent}Thumbnail data size: {len(ifd_data)} bytes")
            continue
            
        # Process the IFD if it contains data
        if ifd_data:
            process_ifd(ifd_name, ifd_data, exif_dict, indent_level, verbose)


def analyze_exif(file_path: str, verbose: bool = False):
    """
    Analyze EXIF data from an image file and print it in a formatted way.
    
    Parameters:
        file_path (str): Path to the file to analyze.
        verbose (bool): Whether to display detailed information including tag details.
    """
    print(f"\nAnalyzing EXIF data for: {file_path}")
    
    try:
        # Load EXIF data using piexif
        exif_dict = piexif.load(file_path)
        
        if not any(exif_dict.values()):
            print("  No EXIF data found in this file.")
            return
        
        # Process all IFDs in the EXIF dictionary
        process_exif_dict(exif_dict, indent_level=1, verbose=verbose)
        
    except piexif.InvalidImageDataError:
        print("  Error: Invalid image data or no EXIF data present.")
    except Exception as e:
        print(f"  Error analyzing EXIF data: {str(e)}")


def main():
    """
    Main function for the EXIF Analyzer.
    
    It parses command-line arguments, retrieves the input files using the appropriate
    methods (command-line or GUI), and processes the files for EXIF data.
    """
    parser = argparse.ArgumentParser(description='Analyze image files for EXIF metadata.')
    parser.add_argument("-f", "--files", nargs="*", default=[], help="Image file(s) to analyze.")
    parser.add_argument("-d", "--dirs", nargs="*", default=[], help="Directory(ies) to analyze (non-recursive).")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output with detailed tag information.")
    args = parser.parse_args()

    files = FilePicker.get_input_files(args)
    if not files:
        print("No valid files provided. Exiting...")
        return

    # Process each file
    for file in files:
        analyze_exif(file, args.verbose)

if __name__ == "__main__":
    main()
