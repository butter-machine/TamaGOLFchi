import os


def convert_ppm_to_frame(file_path):
    """
    Converts a PPM file in P6 format to a frame (1-bit monochrome) for use in frame buffer.
    Returns the frame as a bytearray.
    """
    with open(file_path, 'rb') as f:
        # Read PPM header
        header = f.readline().strip()
        if header != b'P6':
            print(f"Error: {file_path} is not a valid PPM file.")
            return None
        
        # Skip comments
        line = f.readline().strip()
        while line.startswith(b'#'):
            line = f.readline().strip()

        # Get the width and height
        width, height = map(int, line.split())

        # Read the maximum color value (usually 255)
        max_val = int(f.readline().strip())
        if max_val != 255:
            print(f"Error: Unsupported max color value: {max_val}")
            return None

        # Read the pixel data (RGB format: 3 bytes per pixel)
        pixel_data = f.read(width * height * 3)

        # Convert the RGB pixel data to monochrome (1 bit per pixel)
        frame = bytearray(width * height // 8)
        bit_index = 0
        byte_index = 0
        for i in range(0, len(pixel_data), 3):
            # Average the RGB values to get brightness
            r, g, b = pixel_data[i], pixel_data[i+1], pixel_data[i+2]
            brightness = (r + g + b) // 3  # Simple grayscale average
            pixel = 1 if brightness < 128 else 0  # Black if brightness < 128, else white
            
            # Set the appropriate bit in the frame
            if pixel:
                frame[byte_index] |= (1 << (7 - bit_index))

            # Move to the next bit in the byte
            bit_index += 1
            if bit_index == 8:
                bit_index = 0
                byte_index += 1
        
        return frame

def process_folders(input_folder, output_folder):
    """
    Process the input folder, create corresponding .bin files in the output folder,
    and store frames from PPM files in these .bin files.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)
        if os.path.isdir(folder_path):
            output_bin_file = os.path.join(output_folder, f"{folder_name}.bin")

            # Open the binary output file
            with open(output_bin_file, 'wb') as bin_file:
                # Process each PPM file in the subfolder
                for file_name in os.listdir(folder_path):
                    if file_name.endswith('.pbm'):
                        file_path = os.path.join(folder_path, file_name)
                        print(f"Processing {file_path}...")
                        frame = convert_ppm_to_frame(file_path)
                        if frame:
                            bin_file.write(frame)
            print(f"Finished processing folder: {folder_name}")


if __name__ == "__main__":
    # Input and output paths
    input_folder = input("Enter the input folder path: ")
    output_folder = input("Enter the output folder path: ")

    process_folders(input_folder, output_folder)