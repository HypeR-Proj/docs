# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import tempfile
import unittest

from catalog import render


class CatalogTests(unittest.TestCase):
    def test_adding_a_manifest_module_changes_navigation_without_a_top_level_edit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest = root / 'default.xml'
            manifest.write_text('<manifest><project name="kernel" path="kernel"/></manifest>')
            before = render(root, 'default.xml', {'integration': {'repositories': ['HypeR']}})
            self.assertIn('https://hyper-proj.github.io/kernel/', before)
            self.assertIn('not part of the source checkout', before)
            manifest.write_text('<manifest><project name="kernel" path="kernel"/>'
                                '<include name="modules.xml"/></manifest>')
            (root / 'modules.xml').write_text('<manifest><project name="lib-example" path="lib/example"/></manifest>')
            after = render(root, 'default.xml', {})
            self.assertIn('https://hyper-proj.github.io/lib-example/', after)

    def test_nested_includes_are_relative_to_the_manifest_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'groups').mkdir()
            (root / 'default.xml').write_text('<manifest><include name="groups/tools.xml"/></manifest>')
            (root / 'groups/tools.xml').write_text('<manifest><include name="common.xml"/></manifest>')
            (root / 'common.xml').write_text('<manifest><project name="lib-common" path="lib/common"/></manifest>')
            (root / 'groups/common.xml').write_text('<manifest><project name="wrong-relative-base"/></manifest>')
            rendered = render(root, 'default.xml', {})
            self.assertIn('https://hyper-proj.github.io/lib-common/', rendered)
            self.assertNotIn('wrong-relative-base', rendered)

    def test_includes_cannot_recurse_or_escape_the_manifest_repository(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for include in ('default.xml', '../outside.xml'):
                (root / 'default.xml').write_text(f'<manifest><include name="{include}"/></manifest>')
                with self.assertRaises(ValueError):
                    render(root, 'default.xml', {})


if __name__ == '__main__':
    unittest.main()
