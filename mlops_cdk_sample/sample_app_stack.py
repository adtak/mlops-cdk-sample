import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration, Stack
from constructs import Construct


class SampleAppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        transform_step = tasks.SageMakerCreateTransformJob(
            self,
            "Batch Inference",
            transform_job_name="MyTransformJob",
            model_name="MyModelName",
            model_client_options=tasks.ModelClientOptions(
                invocations_max_retries=3,  # default is 0
                invocations_timeout=Duration.minutes(5),
            ),
            transform_input=tasks.TransformInput(
                transform_data_source=tasks.TransformDataSource(
                    s3_data_source=tasks.TransformS3DataSource(
                        s3_uri="s3://inputbucket/train",
                        s3_data_type=tasks.S3DataType.S3_PREFIX,
                    )
                )
            ),
            transform_output=tasks.TransformOutput(
                s3_output_path="s3://outputbucket/TransformJobOutputPath"
            ),
            transform_resources=tasks.TransformResources(
                instance_count=1,
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.M4, ec2.InstanceSize.XLARGE
                ),
            ),
        )
        success_step = sfn.Succeed(self, id="Succeded")
        definition = transform_step.next(success_step)
        sfn.StateMachine(
            self, "StateMachine", definition=definition, timeout=Duration.minutes(5)
        )
