# Tasks to run the commands, and to develop.
# The commands run with `go run`, so there is no need to build beforehand.
# Pass options with ARGS, as in `make link ARGS="-n -v"`.

.PHONY: status
status:
	@go run . status $(ARGS)

.PHONY: setup
setup:
	@go run . setup $(ARGS)

.PHONY: link
link:
	@go run . link $(ARGS)

.PHONY: unlink
unlink:
	@go run . unlink $(ARGS)

.PHONY: relink
relink:
	@go run . relink $(ARGS)

.PHONY: cleanup
cleanup:
	@go run . cleanup $(ARGS)

.PHONY: test
test:
	go vet ./...
	go test ./...

.PHONY: fmt
fmt:
	gofmt -w main.go internal vault
