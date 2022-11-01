#!/usr/bin/env python3

import aws_cdk as cdk

from mlops_cdk_sample.sm_processing import SageMakerProcessingStack

app = cdk.App()
SageMakerProcessingStack(app, "sample")

app.synth()
