import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration, Size, Stack
from constructs import Construct


class SampleSageMakerTrainingStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, training_params, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        training_step = tasks.SageMakerCreateTrainingJob(
            self,
            "SampleTrainingTask",
            training_job_name=sfn.JsonPath.string_at("$$.Execution.Name"),
            algorithm_specification=tasks.AlgorithmSpecification(
                training_image=tasks.DockerImage.from_ecr_repository(
                    repository=training_params["image_repository"],
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
                                training_params["input_bucket"],
                                "input"
                            ),
                        )
                    ),
                    compression_type=tasks.CompressionType.NONE,
                    input_mode=tasks.InputMode.FILE,
                )
            ],
            output_data_config=tasks.OutputDataConfig(
                s3_output_location=tasks.S3Location.from_bucket(
                    training_params["output_bucket"],
                    "output"
                ),
            ),
            enable_network_isolation=True,
            resource_config=tasks.ResourceConfig(
                instance_count=1,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
                ),
                volume_size=Size.gibibytes(1),
            ),
            role=get_role_sagemaker(self),
        )
        success_step = sfn.Succeed(self, "Succeded")
        definition = training_step.next(success_step)
        sfn.StateMachine(
            self,
            "SampleTrainingStateMachine",
            definition=definition,
            timeout=Duration.minutes(5),
            role=get_role_statemachine(self),
        )


def get_role_statemachine(scope):
    return iam.Role(
        scope,
        "SampleTrainingStateMachineRole",
        assumed_by=iam.ServicePrincipal("states.ap-northeast-1.amazonaws.com"),
        inline_policies={
            "CreateSageMakerTrainingJobPolicy": iam.PolicyDocument(
                statements=[
                    iam.PolicyStatement(
                        actions=["sagemaker:CreateTrainingJob", "iam:PassRole"],
                        effect=iam.Effect.ALLOW,
                        resources=["*"],
                    ),
                ]
            )
        },
    )


def get_role_sagemaker(scope):
    # https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html#sagemaker-roles-createtrainingjob-perms
    return iam.Role(
        scope,
        "SampleSageMakerTrainingJobRole",
        assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        inline_policies={
            "SageMakerProcessingPolicy": iam.PolicyDocument(
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
