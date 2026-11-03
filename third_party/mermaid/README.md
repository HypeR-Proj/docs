<!-- SPDX-FileCopyrightText: 2026 roolrz -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Mermaid browser distribution

Unmodified `dist/mermaid.min.js` and `LICENSE` from Mermaid 11.12.0's
published npm package. The browser bundle includes its upstream dependency
license notices. Preserve them when updating this distribution.

Source: https://github.com/mermaid-js/mermaid/tree/mermaid%4011.12.0
Package: https://registry.npmjs.org/mermaid/-/mermaid-11.12.0.tgz

Published npm integrity, verified before importing:

```
sha512-ZudVx73BwrMJfCFmSSJT84y6u5brEoV8DOItdHomNLz32uBjNrelm7mg95X7g+C6UoQH/W6mBLGDEDv73JdxBg==
```

The documentation builder copies the self-contained browser bundle and license
into every site artifact. No npm installation or CDN download occurs during
site generation or diagram rendering. The documentation module's offline-browser
test verifies the generated site, not just the existence of the JavaScript file.
