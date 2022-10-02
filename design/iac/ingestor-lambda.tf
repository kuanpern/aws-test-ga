# lambda subscription to SNS (for upstream cloud)




    {
      "Sid": "__default_statement_ID",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "SNS:Subscribe"
      ],
      "Resource": "arn:aws:sns:ap-southeast-1:858070140421:s3-access-create-topic",
      "Condition": {
        "StringEquals": {
          "AWS:SourceOwner": "858070140421"
        }
      }
    }