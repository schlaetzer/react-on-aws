#!/usr/bin/env python
# coding: utf-8

import json
import boto3
import zipfile
import io
import mimetypes


def lambda_handler(event, context):
    
    # Topic for SNS
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-central-1:948929446452:deploySchlaetzerWebsite')
    
    
    location={
        "bucketName": "build.schlaetzer.com",
        "objectKey": "buildschlaetzer.zip"
    }
    
    try:
        # get the build job
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]
                    
        print("Building portfolio from "+str(location))
        
        # define s3
        s3 = boto3.resource('s3')
        
        # Buckets
        build_bucket = s3.Bucket(location["bucketName"])
        schlaetzer_bucket = s3.Bucket('schlaetzer.com')
        
        # download zip from s3
        build_zip = io.BytesIO()
        build_bucket.download_fileobj(location["objectKey"], build_zip)
        
        # upload each of the files to the other s3
        with zipfile.ZipFile(build_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                schlaetzer_bucket.upload_fileobj(obj, nm,
                  ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                schlaetzer_bucket.Object(nm).Acl().put(ACL='public-read')
        
        # tell codepipeline that we have been successful with deploying
        if job:
            print("sending pipeline info: "+job["id"])
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
    except:
        topic.publish(Subject='Error when deploying Schlaetzer.com', Message='Website couldn\'t be successfully deployed...')
        raise

    topic.publish(Subject='Schlaetzer.com has been deployed', Message='Website has been successfully deployed')
    
    return {
        'statusCode': 200,
        'body': json.dumps('worked')
    }
