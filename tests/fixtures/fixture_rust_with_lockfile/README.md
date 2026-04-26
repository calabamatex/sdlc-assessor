# fixture_rust_with_lockfile

Clean Rust library that *also* ships a `Cargo.lock`. Used to verify:

1. The `lockfile_missing` finding from SDLC-036 is silenced when a lockfile is present.
2. The `cargo-audit` SAST adapter's `should_run` precondition is met without the dirty-fixture noise.
