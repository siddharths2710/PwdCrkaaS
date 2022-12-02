VERSION=1.0.0
DOCKERUSER=shreyash14s

build:
	docker build -f Dockerfile -t pwdcrkaas-rest .

tag:
	docker tag pwdcrkaas-rest $(DOCKERUSER)/pwdcrkaas-rest:$(VERSION)

push:
	docker tag pwdcrkaas-rest $(DOCKERUSER)/pwdcrkaas-rest:$(VERSION)
	docker push $(DOCKERUSER)/pwdcrkaas-rest:$(VERSION)
	docker tag pwdcrkaas-rest $(DOCKERUSER)/pwdcrkaas-rest:latest
	docker push $(DOCKERUSER)/pwdcrkaas-rest:latest
