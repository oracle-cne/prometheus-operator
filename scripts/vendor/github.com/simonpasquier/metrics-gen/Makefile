.PHONY: build
build:
	go build -o metrics-gen .

.PHONY: test
test: build
	./metrics-gen --api-dir ./example --module github.com/simonpasquier/metrics-gen/example --out-dir ./example/pkg/metrics --metric-namespace datapipeline_operator
	(cd example && go build ./...)
