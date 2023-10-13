SHELL=/bin/bash
.PHONY: install_pre_commit reset_local_tf run_local_tf_plan


# Local Dev Set Up
clean_py_env:
	python -m pip uninstall -y -r <(pip freeze)


install_pre_commit:
	python -m pip install --upgrade pip wheel setuptools
	python -m pip install pre-commit
	pre-commit install


install_py_deps: clean_py_env install_pre_commit
	python -m pip install -e .


# Local Terraform Commands
type = "default"
service = "default"
reset_local_tf:
	rm -f -R ./tf/$(type)/$(service)/terraform/.terraform
	rm -f ./tf/$(type)/$(service)/terraform/.terraform.lock.hcl
	rm -f -R ./tf/$(type)/$(service)/terraform/modules/.terraform
	rm -f ./tf/$(type)/$(service)/terraform/modules/.terraform.lock.hcl
	cd ./tf/$(type)/$(service)/terraform && terraform init


type = "default"
service = "default"
run_local_tf_plan:
	cd ./tf/$(type)/$(service)/terraform && terraform plan && cd ../../


# Local Docker Commands
docker_clean:
	docker system prune -f -a
	docker volume prune -f


type = "default"
service = "default"
build_kdp_image:
	docker build \
		-f ./docker/dockerfiles/$(type)/$(service).dockerfile \
		-t kdp-data-pipeline-$(service) .


service = "default"
enter_kdp_image:
	docker run \
		-v $$HOME/.aws/credentials:/root/.aws/credentials:ro \
		-it kdp-data-pipeline-$(service) /bin/bash


type = "default"
service = "default"
test_lambda: build_kdp_image
	docker run -d -v ~/.aws-lambda-rie:/aws-lambda --name aws-lambda -p 9000:8080 \
		--entrypoint /aws-lambda/aws-lambda-rie \
		kdp-data-pipeline-$(service):latest \
        /usr/local/bin/python -m awslambdaric kdp_data_pipeline.src.build_test_module.handler
