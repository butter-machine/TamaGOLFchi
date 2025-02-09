## How to convert .gif image to animation
1. Convert .gif animation to .pbm P6 format (using [Pixlion Image Converter](https://www.nchsoftware.com/imageconverter/index.html?srsltid=AfmBOopAlCtXWQG9R3IjHTWoFd3L525Q6CH4Wy8IV0WzcV5I9QOWD1Hz), for example).
2. Each gif must be converted as a series of .pbm files named in alpabetical order, for example, first frame - 00.pbm, second - 01.pbm, etc. Place all converted files under the same folder, for example, if we need to convert two gifs - anim1.gif and anim2.gif, the layout must be the following:
- input_folder
    - anim1
        - 00.pbm
        - 01.pbm
        - xx.pbm
    - anim2
        - 00.pbm
        - 01.pbm
        - xx.pbm
3. Run `python tools/bitmap_converter.py` input path to `input_folder` and path to the output folder - as a result the script will generate two files - anim1.bin and anim2.bin that can be used as animations.


## How to upload the project to ESP32
1. Copy a content of src directory to the root directory of the ESP32.
