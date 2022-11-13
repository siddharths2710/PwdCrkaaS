VERSION=1.0.0
DOCKERUSER=siddharths2710

build:
	docker build -f Dockerfile -t demucs-worker .

run: ## Run the demucs spliting the tracks placed in the input folder
	docker run --rm -i \
		--name=demucs \
		-v $(current-dir)input:/data/input \
		-v $(current-dir)output:/data/output \
		-v $(current-dir)models:/data/models \
		demucs-worker \
		"python3 -m demucs.separate --out /data/output \
		/data/input/$(track)"


push:
	docker tag demucs-worker $(DOCKERUSER)/demucs-worker:$(VERSION)
	docker push $(DOCKERUSER)/demucs-worker:$(VERSION)
	docker tag demucs-worker $(DOCKERUSER)/demucs-worker:latest
	docker push $(DOCKERUSER)/demucs-worker:latest
