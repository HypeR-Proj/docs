<!-- SPDX-FileCopyrightText: 2026 roolrz -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# HypeR workspace

This is a repo-managed source workspace. Each module is an independent Git
repository; this directory is not a Git repository. The manifest links this
entry page and the build commands into the workspace root.

Start with the [project overview](https://github.com/HypeR-Proj/HypeR),
[build guide](https://hyper-proj.github.io/HypeR/docs/learn/getting-started.html)
and [module catalog](https://hyper-proj.github.io/manifest/modules.html).
The catalog follows the manifest and links each module's own documentation.
System architecture and generic documentation remain in the HypeR repository;
they are not duplicated in this workspace entry page.

From the workspace root:

```sh
repo status
make prepare OUT="$PWD/out"
make menuconfig OUT="$PWD/out"
make native-initramfs ARCH=aarch64 OUT="$PWD/out"
make test MODULE=kernel OUT="$PWD/out"
```

`make` prepares generated integration files when needed. Build tools live in
`build/system/`; the surrounding `build/` directory contains independent tooling
and catalog repositories. Configuration and generated artifacts belong in `OUT`
(default `out/`). A component can be built from its own checkout with the same
absolute `OUT`, for example `make -C app/top OUT="$PWD/out"`.

Use `repo sync` to update rolling main branches. To select a working manifest
branch, run `repo init -b BRANCH` followed by `repo sync`. Commit changes in the
repository that owns them. Coordinated changes use the
[CI topic workflow](https://github.com/HypeR-Proj/ci/blob/main/docs/topic-controls.md).
