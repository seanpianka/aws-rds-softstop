import time

import boto3


def handler(event, context):
    rds_instance_name = event["rds_instance"]  # "books_db"

    # Determine if CloudWatch Event rule already exists, create if DNE
    cwe_client = boto3.client("events")
    rule_name = f"softstop-{rds_instance_name}"

    if rule_name not in cwe_client.list_rules(NamePrefix=rule_name)["Rules"]:
        # Get current lambda function context's Arn
        lambda_client = boto3.client("lambda")
        lambda_function_name = context.function_name
        lambda_function_arn = lambda_client.get_function(
            FunctionName=lambda_function_name
        )["Configuration"]["FunctionArn"]

        # Create CloudWatch Event rule for initating lambda function
        rule_arn = cwe_client.put_rule(
            Name=rule_name,
            ScheduleExpression="0 12 * * 5",
            State="ENABLED",
            Description='Softstop rds "{rds_instance}", enable/disable instance weekly',
        )["RuleArn"]

        cwe_client.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    "Id": lambda_function_name,
                    "Arn": lambda_function_arn,
                    "Input": rds_instance,
                }
            ],
        )

    rds_client = boto3.client("rds")
    try:
        rds_instance = rds_client.describe_db_instances(
            DBInstanceIdentifier=rds_instance_name
        )["DbInstances"][0]
    except KeyError:
        print(f'Instance "{rds_instance_name}" does not exist.')
        raise

    if rds_instance["DBInstanceStatus"] == "available":
        rds_client.stop_db_instance(DBInstanceIdentifier=rds_instance_name)
    else:
        rds_client.start_db_instance(DBInstanceIdentifier=rds_instance_name)
        while (
            rds_client.describe_db_instances(DBInstanceIdentifier=rds_instance_name)[
                "DbInstances"
            ][0]["DBInstanceStatus"]
            != "available"
        ):
            time.sleep(10)
        rds_client.stop_db_instance(DBInstanceIdentifier=rds_instance_name)
