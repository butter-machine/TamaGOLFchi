## How to convert .gif image to animation (on PC).
1. Install PIL `pip install pillow`.
2. Run `python3 bitmap_converter` <path to dir>`.

- Supports .png, .jpg, .jpeg, and .gif formats.
- Images are automatically converted to monochrome, but they must already contain only black and white pixels.
- Images must not have any alpha-channel variations (i.e., no transparency).
- The input argument is a directory path. The script processes all images in the specified directory with supported
formats and saves the converted files in the same location with a .bin extension.
- For .gif files, the script creates a new directory with the same name as the original .gif. Each frame is saved as a
separate .bin file, named sequentially as 0000.bin, 0001.bin, 0002.bin, etc.

3. Upload animations to ESP32's `/src/animation` and pictures to `/src/ico`.


## How to upload the project to ESP32
1. Copy a content of src directory to the root directory of the ESP32.
