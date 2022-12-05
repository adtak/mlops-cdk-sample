from typing import Any

import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
from aws_cdk import Duration, Stack
from constructs import Construct

from mlops_cdk_sample.preprocessing import (PreProcessingJob,
                                            PreprocessingParams)
from mlops_cdk_sample.training import TrainingJob, TrainingParams


class StepFunctionsStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        preprocessing_params: PreprocessingParams,
        training_params: TrainingParams,
        **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        preprocess_step = PreProcessingJob(self, preprocessing_params).create_task()
        training_step = TrainingJob(self, training_params).create_task()
        success_step = sfn.Succeed(self, "Succeded")
        definition = preprocess_step.next(training_step).next(success_step)
        sfn.StateMachine(
            self,
            "MlopsStateMachine",
            definition=definition,
            timeout=Duration.minutes(5),
            role=self.get_statemachine_role(),
        )

    def get_statemachine_role(self) -> iam.Role:
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
            },
        )
