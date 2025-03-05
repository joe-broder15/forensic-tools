"""
EXIF Analyzer

This script analyzes one or more image files for EXIF metadata.
It provides both command-line and graphical (GUI) interfaces for file or directory selection.

Features:
- Parses image files to extract EXIF metadata
- Allows file selection via command-line flags or GUI
- Displays formatted EXIF data with customizable detail levels
"""
import os
import argparse
import piexif
from typing import Dict, Any, Tuple, List, Optional, Union
from utils.file_picker import FilePicker


# Constants for known sub-IFD pointers
SUB_IFD_POINTERS = {
    34665: "Exif",    # Exif IFD Pointer
    34853: "GPS",     # GPS IFD Pointer
    40965: "Interop"  # Interoperability IFD Pointer
}


def print_bytes_value(indent: str, tag_name: str, value: bytes, 
                     tag_hex: str, tag_type: Optional[str], verbose: bool) -> None:
    """
    Print a bytes value with appropriate formatting.
    
    Args:
        indent: Current indentation string
        tag_name: Name of the tag
        value: Bytes value to print
        tag_hex: Hexadecimal representation of the tag ID
        tag_type: Type of the tag (for verbose mode)
        verbose: Whether to display detailed information
    """
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


def print_rational_value(indent: str, tag_name: str, value: Tuple[int, int], 
                        tag_hex: str, tag_type: Optional[str], verbose: bool) -> None:
    """
    Print a rational value with appropriate formatting.
    
    Args:
        indent: Current indentation string
        tag_name: Name of the tag
        value: Rational value tuple (numerator, denominator)
        tag_hex: Hexadecimal representation of the tag ID
        tag_type: Type of the tag (for verbose mode)
        verbose: Whether to display detailed information
    """
    if value[1] != 0:
        if verbose:
            print(f"{indent}{tag_name}: {value[0]}/{value[1]} ({value[0]/value[1]:.4f}) "
                  f"[Tag ID: {tag_hex}, Type: {tag_type}, Format: rational]")
        else:
            print(f"{indent}{tag_name}: {value[0]}/{value[1]} ({value[0]/value[1]:.4f})")
    else:
        if verbose:
            print(f"{indent}{tag_name}: {value[0]}/0 [Tag ID: {tag_hex}, Type: {tag_type}, Format: rational]")
        else:
            print(f"{indent}{tag_name}: {value[0]}/0")


def print_array_value(indent: str, tag_name: str, value: Union[List, Tuple], 
                     tag_hex: str, tag_type: Optional[str], verbose: bool) -> None:
    """
    Print an array value with appropriate formatting.
    
    Args:
        indent: Current indentation string
        tag_name: Name of the tag
        value: Array value to print
        tag_hex: Hexadecimal representation of the tag ID
        tag_type: Type of the tag (for verbose mode)
        verbose: Whether to display detailed information
    """
    if verbose:
        print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, "
              f"Format: array, Length: {len(value)}]")
    else:
        print(f"{indent}{tag_name}: {value}")


def print_integer_value(indent: str, tag_name: str, value: int, 
                       tag_hex: str, tag_type: Optional[str], verbose: bool) -> None:
    """
    Print an integer value with appropriate formatting.
    
    Args:
        indent: Current indentation string
        tag_name: Name of the tag
        value: Integer value to print
        tag_hex: Hexadecimal representation of the tag ID
        tag_type: Type of the tag (for verbose mode)
        verbose: Whether to display detailed information
    """
    if verbose:
        print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, Format: integer]")
    else:
        print(f"{indent}{tag_name}: {value}")


def print_generic_value(indent: str, tag_name: str, value: Any, 
                       tag_hex: str, tag_type: Optional[str], verbose: bool) -> None:
    """
    Print a generic value with appropriate formatting.
    
    Args:
        indent: Current indentation string
        tag_name: Name of the tag
        value: Value to print
        tag_hex: Hexadecimal representation of the tag ID
        tag_type: Type of the tag (for verbose mode)
        verbose: Whether to display detailed information
    """
    if verbose:
        print(f"{indent}{tag_name}: {value} [Tag ID: {tag_hex}, Type: {tag_type}, "
              f"Format: {type(value).__name__}]")
    else:
        print(f"{indent}{tag_name}: {value}")


def print_tag_value(ifd_name: str, tag: int, value: Any, indent_level: int = 0, verbose: bool = False) -> bool:
    """
    Print a tag and its value with proper indentation and formatting.
    
    Args:
        ifd_name: Name of the IFD containing the tag
        tag: Tag identifier
        value: Tag value
        indent_level: Current indentation level
        verbose: Whether to display detailed information
            
    Returns:
        bool: True if this tag might contain a sub-IFD
    """
    indent = "    " * indent_level
    tag_info = piexif.TAGS.get(ifd_name, {}).get(tag, {})
    tag_name = tag_info.get("name", f"Unknown tag: 0x{tag:04X}")
    tag_hex = f"0x{tag:04X}"
    
    # Get tag type information for verbose mode
    tag_type = tag_info.get("type", "Unknown") if verbose else None
    
    # Format and print the tag value based on its type
    if isinstance(value, bytes):
        print_bytes_value(indent, tag_name, value, tag_hex, tag_type, verbose)
    elif isinstance(value, tuple) and len(value) == 2:
        print_rational_value(indent, tag_name, value, tag_hex, tag_type, verbose)
    elif isinstance(value, (list, tuple)):
        print_array_value(indent, tag_name, value, tag_hex, tag_type, verbose)
    elif isinstance(value, int):
        print_integer_value(indent, tag_name, value, tag_hex, tag_type, verbose)
    else:
        print_generic_value(indent, tag_name, value, tag_hex, tag_type, verbose)
    
    # Return True if this tag might contain a sub-IFD
    return tag in SUB_IFD_POINTERS.keys()


def print_ifd_stats(ifd_dict: Dict[int, Any], indent_level: int, verbose: bool) -> None:
    """
    Print statistics about an IFD in verbose mode.
    
    Args:
        ifd_dict: Dictionary containing IFD data
        indent_level: Current indentation level
        verbose: Whether to display detailed information
    """
    if not verbose:
        return
        
    indent = "    " * indent_level
    item_count = len(ifd_dict)
    print(f"{indent}    [IFD Info: {item_count} tags]")
    
    # Count different types of values
    value_types = {}
    for tag, value in ifd_dict.items():
        value_type = type(value).__name__
        value_types[value_type] = value_types.get(value_type, 0) + 1
    
    # Print value type distribution
    if value_types:
        type_info = ", ".join([f"{count} {type_name}s" for type_name, count in value_types.items()])
        print(f"{indent}    [Value types: {type_info}]")


def process_sub_ifd(ifd_name: str, ifd_dict: Dict[int, Any], 
                   exif_dict: Dict[str, Any], indent_level: int = 0, verbose: bool = False) -> None:
    """
    Process a sub-IFD and its tags.
    
    Args:
        ifd_name: Name of the sub-IFD
        ifd_dict: Dictionary containing sub-IFD data
        exif_dict: Full EXIF dictionary for further sub-IFD lookup
        indent_level: Current indentation level
        verbose: Whether to display detailed information
    """
    # Display additional sub-IFD information in verbose mode
    print_ifd_stats(ifd_dict, indent_level, verbose)
    
    # Process tags in this sub-IFD
    process_tags(ifd_name, ifd_dict, exif_dict, indent_level, verbose)


def process_tags(ifd_name: str, ifd_dict: Dict[int, Any], 
                exif_dict: Dict[str, Any], indent_level: int = 0, verbose: bool = False) -> None:
    """
    Process and print all tags in an IFD.
    
    Args:
        ifd_name: Name of the IFD
        ifd_dict: Dictionary containing tag data
        exif_dict: Full EXIF dictionary for sub-IFD lookup
        indent_level: Current indentation level
        verbose: Whether to display detailed information
    """
    indent = "    " * indent_level
    print(f"{indent}Tags in {ifd_name}:")
    
    for tag, value in ifd_dict.items():
        # Print the tag and check if it's a sub-IFD pointer
        is_sub_ifd_pointer = print_tag_value(ifd_name, tag, value, indent_level + 1, verbose)
        
        # Process sub-IFD if this tag points to one
        if is_sub_ifd_pointer and tag in SUB_IFD_POINTERS:
            sub_ifd_name = SUB_IFD_POINTERS[tag]
            
            if sub_ifd_name in exif_dict and exif_dict[sub_ifd_name]:
                print(f"{indent}    Sub-IFD: {sub_ifd_name}")
                process_sub_ifd(sub_ifd_name, exif_dict[sub_ifd_name], exif_dict, indent_level + 2, verbose)


def process_ifd(ifd_name: str, ifd_dict: Dict[int, Any], 
               exif_dict: Dict[str, Any], indent_level: int = 0, verbose: bool = False) -> None:
    """
    Process an IFD and its tags.
    
    Args:
        ifd_name: Name of the IFD
        ifd_dict: Dictionary containing IFD data
        exif_dict: Full EXIF dictionary for sub-IFD lookup
        indent_level: Current indentation level
        verbose: Whether to display detailed information
    """
    indent = "    " * indent_level
    print(f"{indent}IFD: {ifd_name}")
    
    # Display additional IFD information in verbose mode
    print_ifd_stats(ifd_dict, indent_level, verbose)
    
    # Process tags in this IFD
    process_tags(ifd_name, ifd_dict, exif_dict, indent_level + 1, verbose)
    
    # Check for thumbnail IFD in Exif IFD
    if ifd_name == "Exif" and "thumbnail" in exif_dict:
        print(f"{indent}    Thumbnail data present")


def process_exif_dict(exif_dict: Dict[str, Any], indent_level: int = 0, verbose: bool = False) -> None:
    """
    Process and print all IFDs in the EXIF dictionary.
    
    Args:
        exif_dict: Dictionary containing all EXIF data
        indent_level: Current indentation level
        verbose: Whether to display detailed information
    """
    # Process each IFD in the EXIF dictionary
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


def analyze_exif(file_path: str, verbose: bool = False) -> None:
    """
    Analyze EXIF data from an image file and print it in a formatted way.
    
    Args:
        file_path: Path to the file to analyze
        verbose: Whether to display detailed information including tag details
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
    
    Parses command-line arguments, retrieves input files, and processes them for EXIF data.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Analyze image files for EXIF metadata.')
    parser.add_argument("-f", "--files", nargs="*", default=[], 
                        help="Image file(s) to analyze.")
    parser.add_argument("-d", "--dirs", nargs="*", default=[], 
                        help="Directory(ies) to analyze (non-recursive).")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose output with detailed tag information.")
    args = parser.parse_args()

    # Get input files using FilePicker
    files = FilePicker.get_input_files(args)
    if not files:
        print("No valid files provided. Exiting...")
        return

    # Process each file
    for file in files:
        analyze_exif(file, args.verbose)


if __name__ == "__main__":
    main()
