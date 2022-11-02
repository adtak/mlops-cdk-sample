import aws_cdk.aws_stepfunctions as sfn
from aws_cdk import Duration, Stack
from constructs import Construct


class SampleSageMakerProcessingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        image_uri = kwargs["image_uri"]
        input_s3_uri = kwargs["input_s3_uri"]
        output_s3_uri = kwargs["output_s3_uri"]
        role_arn = ""
        state_json = {
            "Type": "Task",
            "Resource": "arn:aws:states:::aws-sdk:sagemaker:createProcessingJob",
            "Parameters": {
                "AppSpecification": {"ImageUri.$": image_uri},
                "ProcessingJobName": "SamplePreProcessingJob",
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
                            "LocalPath": "/opt/ml/processing/",
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
                                "LocalPath": "/opt/ml/processing/",
                                "S3UploadMode": "EndOfJob",
                                "S3Uri": output_s3_uri,
                            },
                        }
                    ],
                },
                "RoleArn.$": role_arn,
            },
        }
        preprocess_step = sfn.CustomState(
            self, "SamplePreProcessingTask", state_json=state_json
        )
        success_step = sfn.Succeed(self, id="Succeded")
        definition = preprocess_step.next(success_step)
        sfn.StateMachine(
            self,
            "SampleStateMachine",
            definition=definition,
            timeout=Duration.minutes(5),
        )
