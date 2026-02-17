import sys
import os

# Add current directory to path to ensure rlm_manager can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    print("Error: Tkinter is not installed. Please install python3-tk.")
    sys.exit(1)

import rlm_manager

def main():
    # Initialize Tkinter root (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    print("--- RLM License File Inspector ---")
    
    # Open file dialog
    file_path = filedialog.askopenfilename(
        title="Select an RLM License File",
        filetypes=[("License Files", "*.lic *.txt"), ("All Files", "*.*")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    print(f"\nSelected file: {file_path}")

    # Instantiate the manager
    license_file = rlm_manager.RLMLicenseFile()

    try:
        # 1. Read the file
        license_file.read(file_path)
        
        # 2. Dump Header Fields
        print("\n--- Extracted Header Fields ---")
        fields = license_file.get_all_header_fields()
        
        if not fields:
            print("No header fields found (or file format not recognized).")
        else:
            # Print nicely formatted
            max_key_len = max(len(k) for k in fields.keys()) if fields else 0
            for key, value in fields.items():
                print(f"{key.ljust(max_key_len)} : {value}")

        # 3. Dump internal representation status
        print("\n--- Object Info ---")
        print(str(license_file))
        
        # 4. Example of modifying a field (demonstration purposes)
        # We will just print what would happen, to avoid modifying user files without intent
        current_customer = license_file.get_header_field('Customer')
        if current_customer:
            print(f"\nCurrent Customer: {current_customer}")
            print("To update customer, library call would be: license_file.set_header_field('Customer', 'New Name')")

    except FileNotFoundError:
        print(f"Error: The file could not be found: {file_path}")
    except IOError as e:
        print(f"Error: An I/O error occurred: {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()