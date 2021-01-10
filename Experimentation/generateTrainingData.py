import sys, os
from PIL import Image
import matplotlib.pyplot as plt
import numpy

def main():
    try:
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
    except Exception as e:
        print(f"Incorrect parameters: {e}")
        sys.exit()
    
    processData(inputDir, outputDir)

def processData(inputDir, outputDir):
    print("Processing original images...")
    imageCount = 0
    totalImages = 0
    for root, subDirs, files in os.walk(inputDir):
        for file in files:
                totalImages += 1
    totalImages *= 0.6 # Only using images facing directly ahead, slightly left and slightly right, so only 60% of the data
    print(f"Loading {int(totalImages)} images...")
    for root, subDirs, files in os.walk(inputDir):
        for file in files:
            filename = file[:-4] # Trim .JPG from the filename
            if not (filename[6:] == "FL" or filename[6:] == "FR"): # Remove images facing too far left or right
                imageCount += 1
                im = Image.open(os.path.join(root, file)).convert("LA").convert("RGB")
                # plt.imshow(im)
                # plt.show()
                if not (os.path.exists(outputDir)):
                    os.makedirs(outputDir)
                im.save(os.path.join(outputDir, filename)+".bmp", format="BMP")
            print(f"\rProcessed {imageCount} images so far", end="")
    print("\nImages processed.")

if __name__ == "__main__":
    main()