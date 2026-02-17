import os
import re

class RLMLicenseFile:
    """
    A manager for RLM license files.
    Handles reading, writing, and manipulating header comments.
    """

    def __init__(self):
        self._filepath = None
        # Stores the header lines as a list of dictionaries:
        # {'raw': '# Customer: Value', 'key': 'Customer', 'value': 'Value', 'is_comment': True}
        self._header_lines = []
        # Stores the rest of the file content (license data) as raw text
        self._body_content = ""

    def read(self, filename):
        """
        Reads a license file from disk.
        :param filename: Path to the license file.
        :raises FileNotFoundError: If the file does not exist.
        :raises IOError: If the file cannot be read.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f"License file not found: {filename}")

        self._filepath = filename
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except Exception as e:
            raise IOError(f"Failed to read file {filename}: {e}")

        self._header_lines = []
        self._body_content = ""
        
        in_header = True
        
        for line in lines:
            # Header detection: starts with # or is whitespace before the first non-comment line
            if in_header:
                if line.strip().startswith('#'):
                    self._parse_header_line(line)
                elif line.strip() == "":
                    # Preserve empty lines in header
                    self._header_lines.append({'raw': line, 'key': None, 'value': None, 'is_comment': True})
                else:
                    # We hit the first non-comment, non-empty line (Start of body)
                    in_header = False
                    self._body_content += line
            else:
                self._body_content += line

    def _parse_header_line(self, line):
        """
        Parses a single comment line to extract Key: Value pairs.
        """
        # Regex looks for "# Key: Value"
        # Allows for whitespace variations.
        match = re.match(r'^#\s+([^:]+):\s+(.*)$', line.strip())
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            self._header_lines.append({
                'raw': line, 
                'key': key, 
                'value': value, 
                'is_comment': True
            })
        else:
            # Generic comment line (separators, etc.)
            self._header_lines.append({
                'raw': line, 
                'key': None, 
                'value': None, 
                'is_comment': True
            })

    def write(self, filename=None):
        """
        Writes the current state back to a file.
        :param filename: Optional. If provided, writes to a new file. 
                         If None, overwrites the original file.
        :raises ValueError: If no file is associated and no filename is provided.
        """
        target = filename if filename else self._filepath
        
        if not target:
            raise ValueError("No filename specified for writing.")

        try:
            with open(target, 'w', encoding='utf-8') as f:
                # Write Header
                for item in self._header_lines:
                    # If the line was modified via set_header_field, we reconstruct it.
                    # Otherwise, we write the raw original line to preserve formatting.
                    if item['key']:
                        # Reconstruct line: "# Key: Value"
                        # We try to preserve the original indentation look slightly
                        f.write(f"# {item['key']}: {item['value']}\n")
                    else:
                        f.write(item['raw'])
                
                # Write Body
                f.write(self._body_content)
                
        except Exception as e:
            raise IOError(f"Failed to write file {target}: {e}")

    def get_header_field(self, key):
        """
        Retrieves the value of a specific header field.
        :param key: The field name (e.g., 'Customer').
        :return: The field value or None if not found.
        """
        for item in self._header_lines:
            if item['key'] and item['key'].lower() == key.lower():
                return item['value']
        return None

    def set_header_field(self, key, value):
        """
        Sets the value of a header field. 
        If the key exists, it updates it. 
        If not, it appends it to the header.
        
        :param key: The field name.
        :param value: The new value.
        """
        found = False
        for item in self._header_lines:
            if item['key'] and item['key'].lower() == key.lower():
                item['value'] = str(value)
                item['raw'] = f"# {item['key']}: {item['value']}\n" # Update raw representation
                found = True
                break
        
        if not found:
            # Add new field before the end of the header
            # We insert it before the last line (usually the closing #----)
            # or just append if structure is unknown.
            new_entry = {
                'raw': f"# {key}: {value}\n",
                'key': key,
                'value': str(value),
                'is_comment': True
            }
            self._header_lines.append(new_entry)

    def get_all_header_fields(self):
        """
        Returns a dictionary of all parsed header fields.
        """
        fields = {}
        for item in self._header_lines:
            if item['key']:
                fields[item['key']] = item['value']
        return fields

    def __str__(self):
        return f"RLMLicenseFile(path={self._filepath}, fields={len(self.get_all_header_fields())})"