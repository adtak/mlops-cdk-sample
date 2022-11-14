import aws_cdk.aws_ecr as ecr
from aws_cdk import RemovalPolicy, Stack
from constructs import Construct


class SampleECRStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.preprocessing_repository = ecr.Repository(
            self,
            "SamplePreProcessingRepo",
            repository_name="sample-sm-processing",
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.training_repository = ecr.Repository(
            self,
            "SampleTrainingRepo",
            repository_name="sample-sm-training",
            removal_policy=RemovalPolicy.DESTROY,
        )
