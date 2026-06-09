# Build / install entry points for the plugin's compiled component
# (the memgrep memory-recall engine in scripts/memgrep/).
#
# End-users normally never need these: scripts/install-memgrep.sh
# downloads a prebuilt, sha256-verified binary from the GitHub release
# assets. The targets below are the from-source path for contributors
# and for platforms without a prebuilt asset.

.PHONY: build test install clean

build:
	cargo build --release --locked --manifest-path scripts/memgrep/Cargo.toml

test:
	cargo test --locked --manifest-path scripts/memgrep/Cargo.toml

install:
	./scripts/install-memgrep.sh

clean:
	cargo clean --manifest-path scripts/memgrep/Cargo.toml
