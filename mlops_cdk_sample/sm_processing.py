import aws_cdk.aws_stepfunctions as sfn
from aws_cdk import Duration, Stack
from constructs import Construct


class SageMakerProcessingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        state_json = {
            "Type": "Task",
            "Resource": "arn:aws:states:::aws-sdk:sagemaker:createProcessingJob",
            "Parameters": {
                "AppSpecification": {"ImageUri.$": "input_image_uri"},
                "ProcessingJobName": "SamplePreProcessingJob",
                "ProcessingResources": {
                    "ClusterConfig": {
                        "InstanceCount": 1,
                        "InstanceType": "ml.t3.medium",
                        "VolumeSizeInGB": 1,
                    }
                },
                "RoleArn.$": "roler_arn",
            },
            "Next": "NEXT_STATE",
        }
        preprocess_step = sfn.CustomState(
            self, "PreProcessingTask", state_json=state_json
        )
        success_step = sfn.Succeed(self, id="Succeded")
        definition = preprocess_step.next(success_step)
        sfn.StateMachine(
            self, "StateMachine", definition=definition, timeout=Duration.minutes(5)
        )
