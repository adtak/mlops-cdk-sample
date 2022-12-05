from typing import Any

import aws_cdk.aws_ecr_assets as ecr_assets
import cdk_ecr_deployment as ecrdeploy
from aws_cdk import Stack
from constructs import Construct


class PreprocessingImage(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, repository_uri: str, **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        image = ecr_assets.DockerImageAsset(
            self,
            "PreProcessingBuildImage",
            directory="./docker/",
            file="Dockerfile",
            build_args={"tag": "latest"},
            platform=ecr_assets.Platform.LINUX_AMD64,
        )
        ecrdeploy.ECRDeployment(
            self,
            "PreProcessingDeployImage",
            src=ecrdeploy.DockerImageName(image.image_uri),
            dest=ecrdeploy.DockerImageName(repository_uri),
        )
