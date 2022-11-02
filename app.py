#!/usr/bin/env python3

import aws_cdk as cdk
from dotenv import load_dotenv

from mlops_cdk_sample.ecr import SampleECRStack
from mlops_cdk_sample.image import SamplePreprocessingImage
from mlops_cdk_sample.s3 import SampleS3Stack
from mlops_cdk_sample.sm_processing import SampleSageMakerProcessingStack

load_dotenv(".env")

app = cdk.App()
s3_stack = SampleS3Stack(app, "sample-s3")
ecr_stack = SampleECRStack(app, "sample-ecr")
SamplePreprocessingImage(app, "sample-image", ecr_stack.repository.repository_uri)
preprocess_params = {
    "image_uri": ecr_stack.repository.repository_uri_for_tag("latest"),
    "input_s3_uri": s3_stack.input_bucket.s3_url_for_object("input.csv"),
    "output_s3_uri": s3_stack.output_bucket.s3_url_for_object(),
}
SampleSageMakerProcessingStack(
    app, "sample-sm-processing", preprocess_params=preprocess_params
)

app.synth()
