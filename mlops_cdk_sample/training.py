from typing import TypedDict

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_ecr as ecr
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
import aws_cdk as cdk
from constructs import Construct


class TrainingParams(TypedDict):
    input_s3_bucket: s3.IBucket
    output_s3_bucket: s3.IBucket
    image_repository: ecr.IRepository


class TrainingJob:
    def __init__(self, scope: Construct, training_params: TrainingParams) -> None:
        self.scope = scope
        self.training_params = training_params

    def create_task(self) -> tasks.SageMakerCreateTrainingJob:
        return tasks.SageMakerCreateTrainingJob(
            self.scope,
            "TrainingTask",
            training_job_name=sfn.JsonPath.string_at("$$.Execution.Name"),
            algorithm_specification=tasks.AlgorithmSpecification(
                training_image=tasks.DockerImage.from_ecr_repository(
                    repository=self.training_params["image_repository"],
                    tag_or_digest="latest",
                ),
            ),
            input_data_config=[
                tasks.Channel(
                    channel_name="training",
                    data_source=tasks.DataSource(
                        s3_data_source=tasks.S3DataSource(
                            s3_data_type=tasks.S3DataType.S3_PREFIX,
                            s3_location=tasks.S3Location.from_bucket(
                                self.training_params["input_s3_bucket"], "input"
                            ),
                        )
                    ),
                    compression_type=tasks.CompressionType.NONE,
                    input_mode=tasks.InputMode.FILE,
                )
            ],
            output_data_config=tasks.OutputDataConfig(
                s3_output_location=tasks.S3Location.from_bucket(
                    self.training_params["output_s3_bucket"], "output"
                ),
            ),
            enable_network_isolation=True,
            resource_config=tasks.ResourceConfig(
                instance_count=1,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
                ),
                volume_size=cdk.Size.gibibytes(1),
            ),
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
            role=self._get_sagemaker_training_job_role(),
            timeout=cdk.Duration(10),
        )

    def _get_sagemaker_training_job_role(self) -> iam.Role:
        # https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html#sagemaker-roles-createtrainingjob-perms
        return iam.Role(
            self.scope,
            "SageMakerTrainingJobRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            inline_policies={
                "SageMakerTrainingJobPolicy": iam.PolicyDocument(
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
