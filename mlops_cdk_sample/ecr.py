import aws_cdk.aws_ecr as ecr
from aws_cdk import Stack
from constructs import Construct


class ECRStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr.Repository(
            self, "PreProcessingRepo", repository_name="sample-sm-processing"
        )
