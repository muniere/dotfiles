.PHONY: build install clean

build:
	mkdir -p dist
	npx @vscode/vsce package --allow-missing-repository --skip-license --out dist/muniere-vscode-theme-1.0.0.vsix

install: build
	code --install-extension dist/muniere-vscode-theme-1.0.0.vsix

clean:
	rm -rf dist
