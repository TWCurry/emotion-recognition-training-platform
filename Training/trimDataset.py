import os

count = 0
removeCount = 0
for root, subDirs, files in os.walk("."):
    for file in files:
        count +=1
        if count % 2 == 0:
            os.remove(os.path.join(root, file))
            removeCount +=1
            print(f"\rRemoved {removeCount} files so far...")
print(f"\nComplete. Removed {removeCount} files.")