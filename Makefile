.PHONY: format black isort test deploy destroy invoke

format: black isort

black:
				poetry run black . --experimental-string-processing

isort:
				poetry run isort .

mypy:
				poetry run mypy .

test:
				poetry run pytest

deploy:
				poetry run cdk deploy --all

destroy:
				poetry run cdk destroy --all

invoke:
				aws sagemaker-runtime invoke-endpoint --endpoint-name mlops-endpoint --body `echo '{"x1":1, "x2":2}' | base64` output.json
