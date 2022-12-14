# standard library
from datetime import datetime, timedelta
from typing import List, Optional, TypeVar

# pypi/conda library
from boto3 import client

Response = TypeVar("Response")

cw = client("cloudwatch", region_name="eu-west-1")


class CloudWatchMetricsFilter:

    cw = client("cloudwatch", region_name="eu-west-1")

    @classmethod
    def list_log_groups(cls):
        paginator = cls.cw.get_paginator("list_metrics")
        for response in paginator.paginate(
            Dimensions=[{"Name": "LogGroupName"}],
            MetricName="IncomingLogEvents",
            Namespace="AWS/Logs",
        ):
            yield response["Metrics"]

    @classmethod
    def seek_metrics(cls, response: Response, namespace: str, filtered_metrics: Optional[List] = None):
        filtered_metrics = filtered_metrics or []

        for res in response["Metrics"]:
            if f"{namespace}" in res.get("Namespace", "").lower():
                filtered_metrics.append(res)

        return filtered_metrics

    @classmethod
    def filter(cls, namespace: str, filtered_metrics: Optional[List] = None):
        filtered_metrics = []
        response = cls.cw.list_metrics()
        filtered_metrics = cls.seek_metrics(response, namespace)

        while response.get("NextToken"):
            next_token = response.pop("NextToken")
            response = cls.cw.list_metrics(NextToken=next_token)
            filtered_metrics = cls.seek_metrics(response, namespace, filtered_metrics)

        return filtered_metrics


# List all the metric "streams"
cw.list_metric_streams()
# List all the training jobs
cw.list_metrics(Namespace="/aws/sagemaker/TrainingJobs")
# List all the training jobs in the last 3 days. NOTE: Although it looks like the RecentlyActive option is configurable, HOWEVER, it takes ONLY "PT3H" as value. So don't waste your time to try some other values...
cw.list_metrics(Namespace="/aws/sagemaker/TrainingJobs", RecentlyActive="PT3H")


# fetch all sagemaker metrics
sagemaker_metrics = CloudWatchMetricsFilter.filter(namespace="sagemaker")


# Get metric statistics
stats = cw.get_metric_statistics(
    Namespace="AWS/SageMaker",
    MetricName="ModelLatency",
    Dimensions=[
        {"Name": "EndpointName", "Value": "endpoint-name"},
        {"Name": "VariantName", "Value": "AllTraffic"},
    ],
    StartTime=datetime.utcnow() - timedelta(days=3),
    EndTime=datetime.utcnow(),
    Period=3600,
    Statistics=[
        "Average",
        "Sum",
        "Minimum",
        "Maximum",
    ],
)

# Get endpoint metrics
response = cw.get_metric_data(
    MetricDataQueries=[
        {
            "Id": "modellatency",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SageMaker",
                    "MetricName": "ModelLatency",
                    "Dimensions": [
                        {"Name": "EndpointName", "Value": "endpoint-name"},
                        {"Name": "VariantName", "Value": "AllTraffic"},
                    ],
                },
                "Period": 3600,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
        {
            "Id": "overheadlatency",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SageMaker",
                    "MetricName": "OverheadLatency",
                    "Dimensions": [
                        {"Name": "EndpointName", "Value": "endpoint-name"},
                        {"Name": "VariantName", "Value": "AllTraffic"},
                    ],
                },
                "Period": 3600,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
        {
            "Id": "modelsetuptime",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SageMaker",
                    "MetricName": "ModelSetupTime",
                    "Dimensions": [
                        {"Name": "EndpointName", "Value": "endpoint-name"},
                        {"Name": "VariantName", "Value": "AllTraffic"},
                    ],
                },
                "Period": 3600,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
        {
            "Id": "invocations",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SageMaker",
                    "MetricName": "Invocations",
                    "Dimensions": [
                        {"Name": "EndpointName", "Value": "endpoint-name"},
                        {"Name": "VariantName", "Value": "AllTraffic"},
                    ],
                },
                "Period": 3600,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
    ],
    StartTime=datetime.utcnow() - timedelta(days=3),
    EndTime=datetime.utcnow(),
    ScanBy="TimestampAscending",
)


# get training metrics
response = cw.get_metric_data(
    MetricDataQueries=[
        {
            "Id": "memoryutilization",
            "MetricStat": {
                "Metric": {
                    "Namespace": "/aws/sagemaker/TrainingJobs",
                    "MetricName": "MemoryUtilization",
                    "Dimensions": [
                        {
                            "Name": "Host",
                            "Value": "training-job-name",
                        }
                    ],
                },
                "Period": 60,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
        {
            "Id": "cpuutilization",
            "MetricStat": {
                "Metric": {
                    "Namespace": "/aws/sagemaker/TrainingJobs",
                    "MetricName": "CPUUtilization",
                    "Dimensions": [
                        {
                            "Name": "Host",
                            "Value": "training-job-name",
                        }
                    ],
                },
                "Period": 60,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
        {
            "Id": "diskutilization",
            "MetricStat": {
                "Metric": {
                    "Namespace": "/aws/sagemaker/TrainingJobs",
                    "MetricName": "DiskUtilization",
                    "Dimensions": [
                        {
                            "Name": "Host",
                            "Value": "training-job-name",
                        }
                    ],
                },
                "Period": 60,
                "Stat": "Sum",
            },
            "ReturnData": True,
        },
    ],
    StartTime=datetime.utcnow() - timedelta(days=7),
    EndTime=datetime.utcnow(),
    ScanBy="TimestampAscending",
)
