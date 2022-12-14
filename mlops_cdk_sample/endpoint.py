from typing import TypedDict

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from constructs import Construct


class ModelParams(TypedDict):
    image_repository: ecr.IRepository


class SagemakerModel:
    def __init__(self, scope: Construct, model_params: ModelParams) -> None:
        self.scope = scope
        self.model_params = model_params

    def create_task(self) -> tasks.SageMakerCreateModel:
        return tasks.SageMakerCreateModel(
            self.scope,
            "CreateModelTask",
            model_name=sfn.JsonPath.string_at(
                "States.Format('LinearRegr-{}', $$.Execution.Name)"
            ),
            primary_container=tasks.ContainerDefinition(
                image=tasks.DockerImage.from_ecr_repository(
                    repository=self.model_params["image_repository"],
                    tag_or_digest="latest",
                ),
                mode=tasks.Mode.SINGLE_MODEL,
                # https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html#your-algorithms-inference-code-load-artifacts
                model_s3_location=tasks.S3Location.from_json_expression(
                    "$.ModelArtifacts.S3ModelArtifacts"
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
            "CreateEndpointConfigTask",
            endpoint_config_name=sfn.JsonPath.string_at(
                "States.Format('LinearRegr-EndpointConfig-{}', $$.Execution.Name)"
            ),
            production_variants=[
                tasks.ProductionVariant(
                    instance_type=ec2.InstanceType.of(
                        ec2.InstanceClass.M5,
                        ec2.InstanceSize.LARGE,
                    ),
                    model_name=sfn.JsonPath.string_at(
                        "States.Format('LinearRegr-{}', $$.Execution.Name)"
                    ),
                    variant_name="variant-name-1",
                )
            ],
            integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
            timeout=cdk.Duration.minutes(10),
        )


class SagemakerEndpoint:
    def __init__(self, scope: Construct) -> None:
        self.scope = scope

    def create_task(self) -> tasks.SageMakerCreateEndpoint:
        return tasks.SageMakerCreateEndpoint(
            self.scope,
            "CreateEndpointTask",
            endpoint_name="mlops-endpoint",
            endpoint_config_name=sfn.JsonPath.string_at(
                "States.Format('LinearRegr-EndpointConfig-{}', $$.Execution.Name)"
            ),
            integration_pattern=sfn.IntegrationPattern.REQUEST_RESPONSE,
            timeout=cdk.Duration.minutes(10),
        )
