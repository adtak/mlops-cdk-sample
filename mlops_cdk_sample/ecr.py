from typing import Any

import aws_cdk.aws_ecr as ecr
from aws_cdk import RemovalPolicy, Stack
from constructs import Construct


class ECRStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs: Any) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.preprocessing_repository = ecr.Repository(
            self,
            "PreProcessingRepo",
            repository_name="sm-processing",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.training_repository = ecr.Repository(
            self,
            "TrainingRepo",
            repository_name="sm-training",
            removal_policy=RemovalPolicy.DESTROY,
        )
