<!--
SPDX-FileCopyrightText: 2026 roolrz
SPDX-License-Identifier: Apache-2.0
-->

# Repository documentation

Each repository owns its README and optional detailed guides. HypeR supplies the
system introduction, Quick Start and a catalog linking to the component sites.
Documentation changes belong in the same PR as the implementation they describe.

The Documentation workflow builds only the current repository. PRs validate local
links and source references; a push resulting from a merge to `main` publishes the
site through GitHub Pages. Documentation does not depend on system builds, I/O VM
compilation or Pi5 image generation.

For a `docs` PR, validation executes the candidate tools and builds a complete
site. Other repositories in the same topic select the documentation PR's exact
merge commit; unrelated PRs and main publication use the current main tools.
Ambiguous topics or unavailable merge candidates fail validation instead of
silently checking with older tooling. PR builds use read-only credentials;
publication remains a separate main-only job.

A repository's entry point is `README.md`; additional tracked Markdown files are
published at their existing paths. `documentation.pages` may explicitly select
published Markdown files; both source checks and rendering use this selection.
Hidden, `legacy/` and `third_party/` files are excluded. The entry point must
remain selected. Links to existing nonpublished source files are still allowed.
Root README becomes `index.html`; other pages
use `.html` in place of `.md`. Relative links stay within that repository. Links
to tracked source files point to the owning GitHub repository and exact revision.
Cross-repository links must use an explicit documentation-site or GitHub URL.

Build a site locally from the workspace:

```sh
python3 -m venv /tmp/hyper-docs
/tmp/hyper-docs/bin/pip install -r docs/tools/requirements.txt
/tmp/hyper-docs/bin/python docs/tools/build.py \
  --root kernel --repository kernel --output /tmp/kernel-docs
```

Choose a fresh output directory. The builder checks generated HTML links and
anchors before the site is uploaded. The shared action is provided by `docs`;
`ci` owns the reusable GitHub Actions workflow. Each repository controls when to
invoke it through its own `.github/workflows/publish-docs.yml`.

## Navigation and catalog includes

Pages use their first level-one heading as the default navigation title, with
inline formatting removed. The root README is shown as Overview. Without a
heading, the filename supplies the title and preserves technical capitalization.
Default navigation places Overview first, then technical pages in source-path
order, followed by contribution, conduct, security, license and changelog guides.

A module can set `documentation.nav` in `component.json` to choose titles, order
and groups. Entries use original source paths; the builder handles README's
published rename. Pages omitted from this list are appended with default titles.
Only selected published pages can appear, and a page may appear only once:

```json
{
  "documentation": {
    "nav": [
      {"Introduction": "README.md"},
      {"Architecture": [
        {"I/O isolation": "docs/io-isolation.md"},
        {"SMMUv3": "docs/smmuv3.md"}
      ]}
    ]
  }
}
```

The manifest catalog resolves every XML `include` name from the manifest
repository root, including includes nested inside subdirectories. This matches
`repo` and the build reader; a child file does not change the include base.
Includes must remain inside the repository and cannot form a cycle.
