#!/usr/bin/env python3

import aws_cdk as cdk

from sample_app.sample_app_stack import SampleAppStack

app = cdk.App()
SampleAppStack(app, "sample-app")

app.synth()
