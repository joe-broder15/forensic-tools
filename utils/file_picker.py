"""
File Picker Utility

This module provides a unified interface for file selection operations,
supporting both GUI-based and command-line file/directory selection.
"""
import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog
from typing import List, Optional


class FilePicker:
    """
    A unified class for handling file selection operations.
    
    This class provides methods for selecting files via GUI or command-line arguments,
    supporting both individual file selection and directory-based file collection.
    """
    
    @staticmethod
    def pick_files_gui() -> List[str]:
        """
        Launch a GUI file picker for the user to select files.
        
        Returns:
            List[str]: List of selected file paths.
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        files = list(filedialog.askopenfilenames(title="Select image files to analyze"))
        root.destroy()  # Close the Tkinter instance
        return files

    @staticmethod
    def pick_directory_gui() -> List[str]:
        """
        Launch a GUI directory picker and list files from the selected directory (non-recursively).
        
        Returns:
            List[str]: List of file paths from the selected directory.
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
    
    @staticmethod
    def get_files_from_directory(directory: str) -> List[str]:
        """
        Get all files from a directory (non-recursively).
        
        Args:
            directory (str): Path to the directory
            
        Returns:
            List[str]: List of file paths from the directory
        """
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' is not a valid directory.")
            return []
            
        files = [os.path.join(directory, f) for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f))]
        
        if files:
            print(f"Directory '{directory}' provided with {len(files)} files.")
        else:
            print(f"Directory '{directory}' does not contain any files.")
            
        return files
    
    @classmethod
    def get_input_files(cls, args: argparse.Namespace) -> List[str]:
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
            List[str]: List of file paths to analyze.
        """
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
                gui_files = cls.pick_files_gui()
                if not gui_files:
                    print("No files selected.")
                files.extend(gui_files)
        
        # Process directory flag (-d/--dirs)
        if '-d' in sys.argv or '--dirs' in sys.argv:
            if args.dirs:
                for d in args.dirs:
                    dir_files = cls.get_files_from_directory(d)
                    files.extend(dir_files)
            else:
                print("Directory flag set with no arguments; launching directory picker GUI...")
                gui_dir_files = cls.pick_directory_gui()
                if not gui_dir_files:
                    print("No files found in selected directory.")
                files.extend(gui_dir_files)
        
        # Default to file picker GUI if no flags are provided
        if not any(flag in sys.argv for flag in ('-f', '--files', '-d', '--dirs')):
            print("No command-line arguments provided; using file picker GUI...")
            gui_files = cls.pick_files_gui()
            if not gui_files:
                print("No files selected.")
            files.extend(gui_files)
        
        return files
