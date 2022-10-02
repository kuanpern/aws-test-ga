#!/bin/bash

AWS_PROFILE=localstack
aws --profile ${AWS_PROFILE} configure set aws_access_key_id _
aws --profile ${AWS_PROFILE} configure set aws_secret_access_key _
aws --profile ${AWS_PROFILE} configure set region ap-northeast-1

# Make a S3 bucket and put test data
aws --endpoint-url=http://localstack:4566 --profile ${AWS_PROFILE} s3 mb s3://lambda-test-example --cli-connect-timeout 6000
aws --endpoint-url=http://localstack:4566 --profile ${AWS_PROFILE} s3 cp ./tests/data/c01.csv s3://lambda-test-example --cli-connect-timeout 6000

# Unit Testing
pipenv install -d
pipenv run test

curl -XPOST "http://lambda:8080/2015-03-31/functions/function/invocations" -d @./tests/data/s3_event.json 