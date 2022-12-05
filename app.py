#!/usr/bin/env python3

import aws_cdk as cdk
from dotenv import load_dotenv

from mlops_cdk_sample.ecr import SampleECRStack
from mlops_cdk_sample.image import SamplePreprocessingImage
from mlops_cdk_sample.s3 import SampleS3Stack
from mlops_cdk_sample.preprocessing import SampleSageMakerProcessingStack
from mlops_cdk_sample.training import SampleSageMakerTrainingStack

load_dotenv(".env")

app = cdk.App()
s3_stack = SampleS3Stack(app, "sample-s3")
ecr_stack = SampleECRStack(app, "sample-ecr")
SamplePreprocessingImage(
    app, "sample-image", ecr_stack.preprocessing_repository.repository_uri
)
preprocess_params = {
    "image_uri": ecr_stack.preprocessing_repository.repository_uri_for_tag("latest"),
    "input_s3_uri": s3_stack.processing_input_bucket.s3_url_for_object(),
    "output_s3_uri": s3_stack.processing_output_bucket.s3_url_for_object(),
}
SampleSageMakerProcessingStack(
    app, "sample-sm-processing", preprocess_params=preprocess_params
)
training_params = {
    "image_repository": ecr_stack.training_repository,
    "input_bucket": s3_stack.processing_input_bucket,
    "output_bucket": s3_stack.training_output_bucket,
}
SampleSageMakerTrainingStack(app, "sample-sm-training", training_params=training_params)

app.synth()
