VERSION=1.0.0
DOCKERUSER=siddharths2710

build:
	docker build -f Dockerfile -t pwdcrkaas-worker .

run: ## Run the pwdcrkaas spliting the tracks placed in the input folder
	docker run --rm -i \
		--name=pwdcrkaas \
		-v $(current-dir)input:/data/input \
		-v $(current-dir)output:/data/output \
		pwdcrkaas-worker

push:
	docker tag pwdcrkaas-worker $(DOCKERUSER)/pwdcrkaas-worker:$(VERSION)
	docker push $(DOCKERUSER)/pwdcrkaas-worker:$(VERSION)
	docker tag pwdcrkaas-worker $(DOCKERUSER)/pwdcrkaas-worker:latest
	docker push $(DOCKERUSER)/pwdcrkaas-worker:latest
