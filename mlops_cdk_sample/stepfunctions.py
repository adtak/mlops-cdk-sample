from typing import Any

import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration, Stack
from constructs import Construct

from mlops_cdk_sample.endpoint import (EndpointConfigParams, ModelParams,
                                       SagemakerEndpoint,
                                       SagemakerEndpointConfig, SagemakerModel)
from mlops_cdk_sample.preprocessing import (PreprocessingJob,
                                            PreprocessingParams)
from mlops_cdk_sample.training import TrainingJob, TrainingParams


class StepFunctionsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        preprocessing_params: PreprocessingParams,
        training_params: TrainingParams,
        model_params: ModelParams,
        endpoint_config_params: EndpointConfigParams,
        **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        preprocess_step = PreprocessingJob(self, preprocessing_params).create_task()
        training_step = TrainingJob(self, training_params).create_task()
        model_step = SagemakerModel(self, model_params).create_task()
        endpoint_config_step = SagemakerEndpointConfig(
            self, endpoint_config_params
        ).create_task()
        success_step = sfn.Succeed(self, "Succeded")
        create_endpoint_step = self._create_describe_endpoint().add_catch(
            SagemakerEndpoint(self).create_create_task().next(success_step),
            errors=["SageMaker.SageMakerException"],
        )
        update_endpoint_step = SagemakerEndpoint(self).create_update_task()
        definition = (
            preprocess_step.next(training_step)
            .next(model_step)
            .next(endpoint_config_step)
            .next(create_endpoint_step)
            .next(update_endpoint_step)
            .next(success_step)
        )
        sfn.StateMachine(
            self,
            "MlopsStateMachine",
            state_machine_name="mlops-statemachine",
            definition=definition,
            timeout=Duration.minutes(30),
            role=self._get_statemachine_role(),
        )

    def _get_statemachine_role(self) -> iam.Role:
        return iam.Role(
            self,
            "MlopsStateMachineRole",
            assumed_by=iam.ServicePrincipal("states.ap-northeast-1.amazonaws.com"),
            inline_policies={
                "CreateSageMakerProcessingJobPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["sagemaker:CreateProcessingJob", "iam:PassRole"],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                ),
                "CreateSageMakerProcessingJobSyncPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "sagemaker:DescribeProcessingJob",
                                "sagemaker:StopProcessingJob",
                                "sagemaker:ListTags",
                                "sagemaker:AddTags",
                                "events:PutTargets",
                                "events:PutRule",
                                "events:DescribeRule",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                ),
                "CreateSageMakerTrainingJobPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["sagemaker:CreateTrainingJob", "iam:PassRole"],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                ),
                "CreateSageMakerTrainingJobSyncPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "sagemaker:DescribeTrainingJob",
                                "sagemaker:StopTrainingJob",
                                "sagemaker:ListTags",
                                "sagemaker:AddTags",
                                "events:PutTargets",
                                "events:PutRule",
                                "events:DescribeRule",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                ),
                "CreateEndpointConfigPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=["sagemaker:CreateEndpointConfig", "iam:PassRole"],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                ),
            },
        )

    def _create_describe_endpoint(self) -> tasks.CallAwsService:
        return tasks.CallAwsService(
            self,
            "DescribeEndpointTask",
            service="sagemaker",
            action="describeEndpoint",
            iam_resources=["*"],
            parameters={"EndpointName": "mlops-endpoint"},
        )
