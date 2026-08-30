import xml.etree.ElementTree as ET
import base64
import struct
import os
from gui_file_select import file_selector

# ==========================================
# CONFIGURATION: CHANGE THESE TWO VARIABLES
# ==========================================
mzXML_file = file_selector(("MasSpec Files", "*.mzXML"))
INPUT_FILE = mzXML_file       # Put your exact file name here
OUTPUT_FILE = "output_scaled_mV.mzXML"     # The name of your new scaled file
SCALING_FACTOR = 100                     # Change this to your mV multiplier
# ==========================================

def get_xml_namespace(file_path):
    """Dynamically finds the XML namespace URL inside your specific file."""
    for event, elem in ET.iterparse(file_path, events=('start-ns',)):
        return elem[1]
    return "http://sourceforge.net"

def scale_intensities():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}' in this directory.")
        return

    print(f"Reading {INPUT_FILE}...")
    tree = ET.parse(INPUT_FILE)
    root = tree.getroot()
    
    # Identify namespace to correctly target XML elements
    ns_url = get_xml_namespace(INPUT_FILE)
    ns = {'ns': ns_url}
    
    # Locate every single <peaks> data block in the file
    peaks_elements = root.findall('.//ns:peaks', ns)
    total_peaks = len(peaks_elements)
    
    print(f"Found {total_peaks} scan blocks. Processing scaling to mV...")
    
    for count, peaks in enumerate(peaks_elements, 1):
        if not peaks.text:
            continue
            
        # 1. Decode the Base64 text back into a raw binary string
        encoded_data = base64.b64decode(peaks.text.strip())
        
        # 2. Determine precision format (32-bit float or 64-bit double)
        precision = peaks.attrib.get('precision', '32')
        byte_order = peaks.attrib.get('byteOrder', 'network')
        
        # Network byte order means Big-Endian ('>')
        endian = '>' if byte_order == 'network' else '<'
        
        if precision == '32':
            fmt_char = 'f'
            bytes_per_num = 4
        else:
            fmt_char = 'd'
            bytes_per_num = 8
            
        num_elements = len(encoded_data) // bytes_per_num
        struct_format = f"{endian}{num_elements}{fmt_char}"
        
        # 3. Unpack binary bytes into a readable list of floats
        data_list = list(struct.unpack(struct_format, encoded_data))
        
        # 4. Modify values (mzXML alternates: index 0=m/z, index 1=intensity, 2=m/z, 3=intensity...)
        # We start loop at index 1 and skip by 2 to target ONLY intensities
        for i in range(1, len(data_list), 2):
            data_list[i] = data_list[i] * SCALING_FACTOR
            
        # 5. Pack the floats back into binary bytes
        packed_data = struct.pack(struct_format, *data_list)
        
        # 6. Re-encode back into Base64 text and update the XML element
        peaks.text = base64.b64encode(packed_data).decode('utf-8')
        
        if count % 500 == 0 or count == total_peaks:
            print(f"  Processed {count}/{total_peaks} scans...")

    print(f"Writing scaled data out to {OUTPUT_FILE}...")
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print("Done! File generated successfully.")

if __name__ == "__main__":
    scale_intensities()