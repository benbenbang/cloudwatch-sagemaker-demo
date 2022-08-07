# SageMaker x CloudWatch x Boto3 Demo

## Tips:
1. If you're not sure what can be fetched for sagemaker, check this [doc](https://docs.aws.amazon.com/sagemaker/latest/dg/monitoring-cloudwatch.html)
2. The "Dimension" can be easily found [here](https://eu-west-1.console.aws.amazon.com/cloudwatch/home?region=eu-west-1)
3. Debug: If get empty result, try:
    - remove "unit"
    - stat "sum" or "count"
    - check the "namespace" is right
    - check the starttime and endtime are covering the data points
    - the metric you're looking for is indeed in the namespace
