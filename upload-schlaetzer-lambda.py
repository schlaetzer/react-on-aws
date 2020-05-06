#!/usr/bin/env python
# coding: utf-8

import boto3
import zipfile
import io


s3 = boto3.resource('s3')


# Buckets
build_bucket = s3.Bucket('build.schlaetzer.com')
schlaetzer_bucket = s3.Bucket('schlaetzer.com')

# download zip from s3
build_zip = io.BytesIO()
build_bucket.download_fileobj('buildschlaetzer.zip', build_zip)

# upload each of the files to the other s3
with zipfile.ZipFile(build_zip) as myzip:
    for nm in myzip.namelist():
        obj = myzip.open(nm)
        schlaetzer_bucket.upload_fileobj(obj, nm)
        schlaetzer_bucket.Object(nm).Acl().put(ACL='public-read')