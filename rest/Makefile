VERSION=1.0.0
DOCKERUSER=siddharths2710

build:
	docker build -f Dockerfile-rest -t pwdcrkaas-rest .

push:
	docker tag pwdcrkaas-rest $(DOCKERUSER)/pwdcrkaas-rest:$(VERSION)
	docker push $(DOCKERUSER)/pwdcrkaas-rest:$(VERSION)
	docker tag pwdcrkaas-rest $(DOCKERUSER)/pwdcrkaas-rest:latest
	docker push $(DOCKERUSER)/pwdcrkaas-rest:latest
