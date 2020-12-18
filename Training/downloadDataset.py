import boto3
import os

def downloadDirectoryFroms3(bucketName, remoteDirectoryName):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucketName)
    for obj in bucket.objects.filter(Prefix = remoteDirectoryName):
if not os.path.exists(os.path.dirname(obj.key)):
os.makedirs(os.path.dirname(obj.key))
print("\rDownloading" + obj.key, end="")
bucket.download_file(obj.key, obj.key) # save to same path

downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "AF")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "AN")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "DI")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "HA")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "NE")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "SA")
downloadDirectoryFroms3("twcurry-kdef-dataset-sample", "SU")