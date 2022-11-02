import aws_cdk.aws_ecr_assets as ecr_assets
from aws_cdk import Stack
from constructs import Construct


class SamplePreprocessingImage(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        ecr_assets.DockerImageAsset(
            self,
            "SamplePreProcessingBuildImage",
            directory="./docker/",
            file="Dockerfile",
            target="latest",
        )
