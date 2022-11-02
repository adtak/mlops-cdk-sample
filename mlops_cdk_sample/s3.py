from typing import Any, Dict

import aws_cdk.aws_s3 as s3
from aws_cdk import RemovalPolicy, Stack
from constructs import Construct


class SampleS3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.input_bucket = s3.Bucket(
            self, "SampleInputBucket", **_create_bucket_params()
        )
        self.output_bucket = s3.Bucket(
            self, "SampleOutputBucket", **_create_bucket_params()
        )


def _create_bucket_params() -> Dict[str, Any]:
    return {
        "removal_policy": RemovalPolicy.DESTROY,
        "auto_delete_objects": True,
        "block_public_access": s3.BlockPublicAccess.BLOCK_ALL,
        "bucket_key_enabled": False,
        "bucket_name": "sample-sm-processing-input",
        "encryption": s3.BucketEncryption.S3_MANAGED,
        "object_ownership": s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        "public_read_access": False,
        "versioned": False,
    }
