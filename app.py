#!/usr/bin/env python3

import aws_cdk as cdk

from mlops_cdk_sample.sm_processing import SampleSageMakerProcessingStack

app = cdk.App()
SampleSageMakerProcessingStack(app, "sample")

app.synth()
