from typing import Any, Dict, TypedDict

import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_stepfunctions as sfn
from constructs import Construct


class PreprocessingParams(TypedDict):
    input_s3_bucket: s3.IBucket
    output_s3_bucket: s3.IBucket
    image_repository: ecr.IRepository


class PreProcessingJob:
    def __init__(
        self, scope: Construct, preprocess_params: PreprocessingParams
    ) -> None:
        self.scope = scope
        self.preprocessing_params = preprocess_params

    def create_task(self) -> sfn.CustomState:
        return sfn.CustomState(
            self.scope,
            "SamplePreProcessingTask",
            state_json=self._create_processing_job_state(),
        )

    def _create_processing_job_state(self) -> Dict[str, Any]:
        return {
            "Type": "Task",
            "Resource": "arn:aws:states:::sagemaker:createProcessingJob.sync",
            "Parameters": {
                "AppSpecification": {
                    "ImageUri": self.preprocessing_params[
                        "image_repository"
                    ].repository_uri_for_tag("latest")
                },
                "ProcessingJobName.$": "States.Format('PreProcessingJob-{}', $$.Execution.Name)",  # noqa: E501
                "ProcessingResources": {
                    "ClusterConfig": {
                        "InstanceCount": 1,
                        "InstanceType": "ml.t3.medium",
                        "VolumeSizeInGB": 1,
                    }
                },
                "ProcessingInputs": [
                    {
                        "InputName": "PreProcessingJobInput",
                        "S3Input": {
                            "LocalPath": "/opt/ml/processing/input",
                            "S3CompressionType": "None",
                            "S3DataType": "S3Prefix",
                            "S3InputMode": "File",
                            "S3Uri": self.preprocessing_params[
                                "input_s3_bucket"
                            ].url_for_object(),
                        },
                    }
                ],
                "ProcessingOutputConfig": {
                    "Outputs": [
                        {
                            "OutputName": "SamplePreProcessingJobOutput",
                            "S3Output": {
                                "LocalPath": "/opt/ml/processing/output",
                                "S3UploadMode": "EndOfJob",
                                "S3Uri": self.preprocessing_params[
                                    "output_s3_bucket"
                                ].url_for_object(),
                            },
                        }
                    ],
                },
                "RoleArn": self._get_sagemaker_processing_job_role().role_arn,
            },
        }

    def _get_sagemaker_processing_job_role(self) -> iam.Role:
        # https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html#sagemaker-roles-createprocessingjob-perms
        return iam.Role(
            self.scope,
            "SageMakerProcessingJobRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            inline_policies={
                "SageMakerProcessingJobPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "cloudwatch:PutMetricData",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                                "logs:CreateLogGroup",
                                "logs:DescribeLogStreams",
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:ListBucket",
                                "ecr:GetAuthorizationToken",
                                "ecr:BatchCheckLayerAvailability",
                                "ecr:GetDownloadUrlForLayer",
                                "ecr:BatchGetImage",
                            ],
                            effect=iam.Effect.ALLOW,
                            resources=["*"],
                        ),
                    ]
                )
            },
        )
