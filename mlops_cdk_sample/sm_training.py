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
                    repository=training_params["training_image_repo"],
                    tag_or_digest="latest",
                ),
            ),
            input_data_config=[],
            output_data_config=[],
            enable_network_isolation=True,
            resource_config=tasks.ResourceConfig(
                instance_count=1,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
                ),
                volume_size=Size.gibibytes(1),
            ),
            role="",
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
