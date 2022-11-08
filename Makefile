.DEFAULT_GOAL := bootstrap

.PHONY: bootstrap
bootstrap: 
	@./.bin/bootstrap

.PHONY: link
link:
	@./xake link

.PHONY: unlink
unlink:
	@./xake unlink

.PHONY: cleanup
cleanup:
	@./xake cleanup
