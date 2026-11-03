<!-- SPDX-FileCopyrightText: 2026 roolrz -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# HypeR documentation tools

Shared rendering, source-link checks, themes, navigation and publication tools.
Documentation source stays in the repository that owns the documented behavior.
These tools do not prepare a system workspace, build a kernel or require an SDK.

[WORKSPACE.md](WORKSPACE.md) is the thin entry page linked by the manifest to a
synced workspace's root README. It points to the generic HypeR documentation and
generated module catalog; it does not maintain another copy of either.

```sh
python3 -m pip install -r tools/requirements.txt
python3 tools/check-source.py /path/to/repository
python3 tools/build.py --root /path/to/repository --repository example --output /path/to/out/docs/example
```

The output must be a new directory. System build entries use OUT/docs; standalone
invocations select their output explicitly. CI publishes each repository after
main merges using `.github/actions/documentation`.
