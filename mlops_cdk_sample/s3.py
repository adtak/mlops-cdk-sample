from typing import Any, Dict

import aws_cdk.aws_s3 as s3
from aws_cdk import RemovalPolicy, Stack
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.processing_input_bucket = s3.Bucket(
            self,
            "PreProcessingInputBucket",
            **_create_bucket_params("mlops-preprocessing-input")
        )
        self.processing_output_bucket = s3.Bucket(
            self,
            "PreProcessingOutputBucket",
            **_create_bucket_params("mlops-preprocessing-output")
        )
        self.training_output_bucket = s3.Bucket(
            self,
            "TrainingOutputBucket",
            **_create_bucket_params("mlops-training-output")
        )
        self.capture_data_bucket = s3.Bucket(
            self, "CaptureDataBucket", **_create_bucket_params("mlops-capture-data")
        )


def _create_bucket_params(bucket_name: str) -> Dict[str, Any]:
    return {
        "removal_policy": RemovalPolicy.DESTROY,
        "auto_delete_objects": True,
        "block_public_access": s3.BlockPublicAccess.BLOCK_ALL,
        "bucket_key_enabled": False,
        "bucket_name": bucket_name,
        "encryption": s3.BucketEncryption.S3_MANAGED,
        "object_ownership": s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        "public_read_access": False,
        "versioned": False,
    }
