import boto3
import os

def downloadS3Directory(bucketName, remoteDirectoryName):
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(bucketName)
    for obj in bucket.objects.filter(Prefix = remoteDirectoryName):
        if not os.path.exists(os.path.dirname(obj.key)):
            os.makedirs(os.path.dirname(obj.key))
        print("\rDownloading" + obj.key, end="")
        bucket.download_file(obj.key, obj.key) # save to same path

downloadS3Directory("twcurry-kdef-dataset-sample", "AF")
downloadS3Directory("twcurry-kdef-dataset-sample", "AN")
downloadS3Directory("twcurry-kdef-dataset-sample", "DI")
downloadS3Directory("twcurry-kdef-dataset-sample", "HA")
downloadS3Directory("twcurry-kdef-dataset-sample", "NE")
downloadS3Directory("twcurry-kdef-dataset-sample", "SA")
downloadS3Directory("twcurry-kdef-dataset-sample", "SU")