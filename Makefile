build:
	docker build -t andrchalov/pgnotifyfwd .

run:
	docker run --rm -it \
		--env-file ./env.ini \
		andrchalov/pgnotifyfwd

push:
	docker push andrchalov/pgnotifyfwd
