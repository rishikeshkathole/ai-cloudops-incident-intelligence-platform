import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')

response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-02a88d91a43e460ad'
        },
    ],
    StartTime=datetime.utcnow() - timedelta(minutes=30),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average']
)

print(response)
