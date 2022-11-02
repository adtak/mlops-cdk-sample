from typing import Any, Dict

import aws_cdk.aws_s3 as s3
from aws_cdk import Stack
from constructs import Construct


class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        s3.Bucket(self, "SampleInputBucket", **_create_bucket_params())
        s3.Bucket(self, "SampleOutputBucket", **_create_bucket_params())


def _create_bucket_params() -> Dict[str, Any]:
    return {
        "auto_delete_objects": True,
        "block_public_access": s3.BlockPublicAccess.BLOCK_ALL,
        "buket_key_enabled": False,
        "bucket_name": "sample-sm-processing-input",
        "encryption": s3.BucketEncryption.S3_MANAGED,
        "object_ownership": s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        "public_read_access": False,
        "versioned": False,
    }
