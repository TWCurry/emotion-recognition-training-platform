import os, sys
from PIL import Image

emotionCodes = ["AF", "AN", "DI", "HA", "NE", "SA", "SU"]

def main():
    try:
        inputDir = sys.argv[1]
        outputDir = sys.argv[2]
    except Exception as e:
        print(f"Invalid parameters: {e}")
        sys.exit(1)

    # Create output directory if it does not exist
    if not (os.path.exists(outputDir)):
        os.makedirs(outputDir)

    # Create emotion directories (if they don't exist)
    for emotion in emotionCodes:
        if not (os.path.exists(os.path.join(outputDir, emotion))):
            os.makedirs(os.path.join(outputDir, emotion))

    for root, subDirs, files in os.walk(inputDir):
        for file in files:
            if len(file) == 11: # Straight ahead image
                imageDir = "S"
                emotionCode = file[4:-5]
            else:
                imageDir = file[6:-4]
                emotionCode = file[4:-6]
            if not (emotionCode in emotionCodes):
                print(f"Warning: emotion code {emotionCode} not known.")
                print(f"File: {file}")
            else:
                if not (imageDir == "FL" or imageDir == "FR"): # Remove images facing too far left or right
                    im = Image.open(os.path.join(root, file))
                    im.save(os.path.join(outputDir, emotionCode, file)) # Save images in appropriate folder per emotion

if __name__ == "__main__":
    main()