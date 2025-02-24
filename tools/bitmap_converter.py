"""
A tool for converting images and animations to bitmap format for the device.

- Supports .png, .jpg, .jpeg, and .gif formats.
- Images are automatically converted to monochrome, but they must already contain only black and white pixels.
- Images must not have any alpha-channel variations (i.e., no transparency).
- The input argument is a directory path. The script processes all images in the specified directory with supported
formats and saves the converted files in the same location with a .bin extension.
- For .gif files, the script creates a new directory with the same name as the original .gif. Each frame is saved as a
separate .bin file, named sequentially as 0000.bin, 0001.bin, 0002.bin, etc.
"""


from PIL import Image
import argparse
import os

def image_to_hex(image_path, output_path):
    with Image.open(image_path) as img:
        if img.format == 'GIF':
            byte_array = []
            # Create a folder for the gif if it doesn't exist
            folder_name = os.path.splitext(os.path.basename(image_path))[0]
            output_folder = os.path.join(os.path.dirname(image_path), folder_name)
            os.makedirs(output_folder, exist_ok=True)

            for frame in range(img.n_frames):
                img.seek(frame)
                img_frame = img.convert("1")
                width, height = img_frame.size
                frame_bytes = bytearray()

                for y in range(height):
                    byte = 0
                    for x in range(width):
                        pixel = 0 if img_frame.getpixel((x, y)) else 1
                        byte = (byte << 1) | pixel
                        if (x + 1) % 8 == 0 or x == width - 1:
                            frame_bytes.append(byte)
                            byte = 0
                frame_filename = f"{frame:04d}.bin"
                frame_output_path = os.path.join(output_folder, frame_filename)
                with open(frame_output_path, 'wb') as f:
                    f.write(frame_bytes)

        else:
            img = img.convert("1")
            width, height = img.size
            byte_array = bytearray()
            
            for y in range(height):
                byte = 0
                for x in range(width):
                    pixel = 0 if img.getpixel((x, y)) else 1
                    byte = (byte << 1) | pixel
                    if (x + 1) % 8 == 0 or x == width - 1:
                        byte_array.append(byte)
                        byte = 0
            with open(output_path, 'wb') as f:
                f.write(byte_array)

def process_folder(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            input_path = os.path.join(folder_path, file_name)
            if file_name.lower().endswith('.gif'):
                image_to_hex(input_path, None)
            else:
                output_path = os.path.splitext(input_path)[0] + ".bin"
                image_to_hex(input_path, output_path)
            print(f"Converted: {input_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert images in a folder to raw binary bytes with reversed colors.")
    parser.add_argument("folder", help="Path to the folder containing image files (PNG, JPEG, or GIF)")
    
    args = parser.parse_args()
    process_folder(args.folder)
