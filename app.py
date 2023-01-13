#!/usr/bin/env python3

import aws_cdk as cdk
from dotenv import load_dotenv

from mlops_cdk_sample.ecr import ECRStack
from mlops_cdk_sample.endpoint import EndpointConfigParams, ModelParams
from mlops_cdk_sample.image import (PredictImage, PreprocessingImage,
                                    TrainingImage)
from mlops_cdk_sample.preprocessing import PreprocessingParams
from mlops_cdk_sample.s3 import S3Stack
from mlops_cdk_sample.stepfunctions import StepFunctionsStack
from mlops_cdk_sample.training import TrainingParams

load_dotenv(".env")

app = cdk.App()
s3_stack = S3Stack(app, "mlops-s3")
ecr_stack = ECRStack(app, "mlops-ecr")
PreprocessingImage(
    app, "preprocessing-image", ecr_stack.preprocessing_repository.repository_uri
)
TrainingImage(app, "training-image", ecr_stack.training_repository.repository_uri)
PredictImage(app, "predict-image", ecr_stack.predict_repository.repository_uri)
preprocessing_params: PreprocessingParams = {
    "image_repository": ecr_stack.preprocessing_repository,
    "input_s3_bucket": s3_stack.processing_input_bucket,
    "output_s3_bucket": s3_stack.processing_output_bucket,
}
training_params: TrainingParams = {
    "image_repository": ecr_stack.training_repository,
    "input_s3_bucket": s3_stack.processing_output_bucket,
    "output_s3_bucket": s3_stack.training_output_bucket,
}
model_params: ModelParams = {
    "image_repository": ecr_stack.predict_repository,
}
endpoint_config_params: EndpointConfigParams = {
    "capture_data_s3_bucket": s3_stack.capture_data_bucket,
}
StepFunctionsStack(
    app,
    "mlops-sfn",
    preprocessing_params=preprocessing_params,
    training_params=training_params,
    model_params=model_params,
    endpoint_config_params=endpoint_config_params,
)

app.synth()
