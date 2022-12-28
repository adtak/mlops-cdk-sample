from typing import TypedDict

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from constructs import Construct


class ModelParams(TypedDict):
    input_s3_bucket: s3.IBucket
    image_repository: ecr.IRepository


class SagemakerModel:
    def __init__(self, scope: Construct, model_params: ModelParams) -> None:
        self.scope = scope
        self.model_params = model_params

    def create_task(self) -> tasks.SageMakerCreateModel:
        input_s3_bucket_url = self.model_params["input_s3_bucket"].s3_url_for_object()
        return tasks.SageMakerCreateModel(
            self.scope,
            "CreateModelTask",
            model_name="LinearRegr",
            primary_container=tasks.ContainerDefinition(
                image=tasks.DockerImage.from_ecr_repository(
                    repository=self.model_params["image_repository"],
                    tag_or_digest="latest",
                ),
                mode=tasks.Mode.SINGLE_MODEL,
                # https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html#your-algorithms-inference-code-load-artifacts
                model_s3_location=tasks.S3Location.from_json_expression(
                    f"States.Format('{input_s3_bucket_url}/{{}}/output/model.tar.gz',"
                    " $$.Execution.Name)"
                ),
            ),
            integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
            timeout=cdk.Duration.minutes(10),
        )


class SagemakerEndpointConfig:
    def __init__(self, scope: Construct) -> None:
        self.scope = scope

    def create_task(self) -> tasks.SageMakerCreateEndpointConfig:
        return tasks.SageMakerCreateEndpointConfig(
            self.scope,
            "SagemakerEndpointConfig",
            endpoint_config_name="MlopsEndpointConfig",
            production_variants=[
                tasks.ProductionVariant(
                    initial_instance_count=1,
                    instance_type=ec2.InstanceType.of(
                        ec2.InstanceClass.M5,
                        ec2.InstanceSize.LARGE,
                    ),
                    model_name="MyModel",
                    variant_name="",
                )
            ],
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            timeout=cdk.Duration.minutes(10),
        )


class SagemakerEndpoint:
    def __init__(self, scope: Construct) -> None:
        self.scope = scope

    def create_task(self) -> tasks.SageMakerCreateEndpoint:
        return tasks.SageMakerCreateEndpoint(
            self.scope,
            "SagemakerEndpoint",
            endpoint_name="mlops-endpoint",
            endpoint_config_name=sfn.JsonPath.string_at("$.EndpointConfigName"),
            integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
            timeout=cdk.Duration.minutes(5),
        )
