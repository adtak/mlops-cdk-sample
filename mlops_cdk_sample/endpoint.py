from typing import Any, Dict, TypedDict

import aws_cdk as cdk
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from constructs import Construct


class ModelParams(TypedDict):
    image_repository: ecr.IRepository


class EndpointConfigParams(TypedDict):
    capture_data_s3_bucket: s3.IBucket


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
            role=self._get_sagemaker_model_role(),
            timeout=cdk.Duration.minutes(10),
        )

    def _get_sagemaker_model_role(self) -> iam.Role:
        return iam.Role(
            self.scope,
            "SageMakerModelRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            inline_policies={
                "SageMakerModelPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cloudwatch:PutMetricData",
                                "ecr:GetAuthorizationToken",
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:DescribeLogStreams",
                                "logs:PutLogEvents",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:BatchGetImage",
                                "ecr:GetDownloadUrlForLayer",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=[
                                self.model_params["image_repository"].repository_arn
                            ],
                        ),
                        iam.PolicyStatement(
                            actions=[
                                "ecr:GetAuthorizationToken",
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:ListBucket",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                )
            },
        )


class SagemakerEndpointConfig:
    def __init__(
        self, scope: Construct, endpoint_config_params: EndpointConfigParams
    ) -> None:
        self.scope = scope
        self.endpoint_config_params = endpoint_config_params

    def create_task(self) -> sfn.CustomState:
        return sfn.CustomState(
            self.scope,
            "CreateEndpointConfigTask",
            state_json=self._create_state_json(),
        )

    def _create_state_json(self) -> Dict[str, Any]:
        return {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createEndpointConfig",
            "Parameters": {
                "EndpointConfigName.$": (
                    "States.Format('LinearRegr-EndpointConfig-{}', $$.Execution.Name)"
                ),
                "ProductionVariants": [
                    {
                        "InitialInstanceCount": 1,
                        "InstanceType": "ml.t2.medium",
                        "ModelName.$": (
                            "States.Format('LinearRegr-{}', $$.Execution.Name)"
                        ),
                        "VariantName": "variant-name-1",
                    }
                ],
                "DataCaptureConfig": {
                    "EnableCapture": True,
                    "CaptureOptions": [
                        {"CaptureMode": "Input"},
                        {"CaptureMode": "Output"},
                    ],
                    "DestinationS3Uri": self.endpoint_config_params[
                        "capture_data_s3_bucket"
                    ].s3_url_for_object(),
                    "InitialSamplingPercentage": 100,
                },
            },
        }


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
