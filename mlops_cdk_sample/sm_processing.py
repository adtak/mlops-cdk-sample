from typing import Any, Dict

import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
from aws_cdk import Duration, Stack
from constructs import Construct


class SampleSageMakerProcessingStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, preprocess_params, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        preprocess_step = sfn.CustomState(
            self,
            "SamplePreProcessingTask",
            state_json=_create_processing_job_state(
                preprocess_params["image_uri"],
                preprocess_params["input_s3_uri"],
                preprocess_params["output_s3_uri"],
                get_role_sagemaker(self).role_arn,
            ),
        )
        success_step = sfn.Succeed(self, "Succeded")
        definition = preprocess_step.next(success_step)
        sfn.StateMachine(
            self,
            "SampleStateMachine",
            definition=definition,
            timeout=Duration.minutes(5),
            role=get_role_statemachine(self),
        )


def _create_processing_job_state(
    image_uri, input_s3_uri, output_s3_uri, role_arn
) -> Dict[str, Any]:
    return {
        "Type": "Task",
        "Resource": "arn:aws:states:::aws-sdk:sagemaker:createProcessingJob",
        "Parameters": {
            "AppSpecification": {"ImageUri": image_uri},
            "ProcessingJobName.$": "States.Format('SamplePreProcessingJob-{}', $$.Execution.Name)",  # noqa: E501
            "ProcessingResources": {
                "ClusterConfig": {
                    "InstanceCount": 1,
                    "InstanceType": "ml.t3.medium",
                    "VolumeSizeInGB": 1,
                }
            },
            "ProcessingInputs": [
                {
                    "InputName": "SamplePreProcessingJobInput",
                    "S3Input": {
                        "LocalPath": "/opt/ml/processing/scripts",
                        "S3DataType": "S3Prefix",
                        "S3InputMode": "File",
                        "S3Uri": input_s3_uri,
                    },
                }
            ],
            "ProcessingOutputConfig": {
                "Outputs": [
                    {
                        "OutputName": "SamplePreProcessingJobOutput",
                        "S3Output": {
                            "LocalPath": "/opt/ml/processing/scripts/output",
                            "S3UploadMode": "EndOfJob",
                            "S3Uri": output_s3_uri,
                        },
                    }
                ],
            },
            "RoleArn": role_arn,
        },
    }


def get_role_statemachine(scope):
    return iam.Role(
        scope,
        "SampleStateMachineRole",
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
            )
        },
    )


def get_role_sagemaker(scope):
    return iam.Role(
        scope,
        "SampleSageMakerRole",
        assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        inline_policies={
            "SageMakerProcessingPolicy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=[
                            "s3:ListBucket",
                            "s3:GetObject",
                            "ecr:*",
                        ],
                        effect=iam.Effect.ALLOW,
                        resources=["*"],
                    ),
                ]
            )
        },
    )
