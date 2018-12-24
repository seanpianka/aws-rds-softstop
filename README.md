# aws-rds-softstop

Use CloudWatch Events and a lambda function to periodically enable and disable an RDS instance and practically extend instance disabled time. This script is meant to enable a software bypass for the RDS instance "disabled" state time limit.

## Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "events:ListRules",
                "rds:StopDBInstance",
                "rds:StartDBInstance"
            ],
            "Resource": [
                "arn:aws:events:*:*:rule/*",
                "arn:aws:rds:*:*:db:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "events:PutTargets",
                "lambda:GetFunction",
                "events:PutRule",
                "rds:DescribeDBInstances"
            ],
            "Resource": "*"
        }
    ]
}
```
