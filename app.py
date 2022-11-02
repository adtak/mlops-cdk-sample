#!/usr/bin/env python3

import aws_cdk as cdk

from mlops_cdk_sample.ecr import SampleECRStack
from mlops_cdk_sample.s3 import SampleS3Stack
from mlops_cdk_sample.sm_processing import SampleSageMakerProcessingStack

app = cdk.App()
s3_stack = SampleS3Stack(app, "sample")
SampleECRStack(app, "sample")
kwargs = {
    "input_s3_uri": s3_stack.input_bucket.s3_url_for_object("input.csv"),
    "output_s3_uri": s3_stack.output_bucket.s3_url_for_object(),
}
SampleSageMakerProcessingStack(app, "sample", **kwargs)

app.synth()
