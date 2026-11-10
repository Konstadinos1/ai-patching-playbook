"""Exercise the offline Markdown checker with temporary repositories."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_docs import check_links  # noqa: E402


class DocumentationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name: str, content: str = '') -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def test_relative_file_directory_and_space_links(self) -> None:
        self.write('docs/file with spaces.md', '# Hello world\n')
        self.write('README.md', '[file](docs/file%20with%20spaces.md#hello-world)\n'
                   '[angle](<docs/file with spaces.md>)\n[dir](docs/)\n')
        self.assertEqual(check_links(self.root), [])

    def test_broken_link_reports_source_and_line(self) -> None:
        self.write('README.md', '# Intro\n[missing](missing.md)\n')
        errors = check_links(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn('README.md:2', errors[0])
        self.assertIn('target does not exist', errors[0])

    def test_anchors_and_duplicate_headings(self) -> None:
        self.write('README.md', '# Title\n# Title\n<a id="custom"></a>\n'
                   '[one](#title) [two](#title-1) [three](#custom)\n')
        self.assertEqual(check_links(self.root), [])

    def test_missing_anchor_is_error(self) -> None:
        self.write('README.md', '# Title\n[bad](#missing)\n')
        self.assertIn('heading/anchor #missing does not exist', check_links(self.root)[0])

    def test_fenced_examples_and_external_links_are_ignored(self) -> None:
        self.write('README.md', '```markdown\n[example](missing.md)\n```\n'
                   '~~~\n[example](also-missing.md)\n~~~\n'
                   '[web](https://example.test/missing)\n[mail](mailto:example@example.test)\n')
        self.assertEqual(check_links(self.root), [])

    def test_escaping_and_symlink_targets_are_errors(self) -> None:
        self.write('README.md', '[outside](../outside.md)\n[link](link.md)\n')
        self.write('inside.md')
        (self.root / 'link.md').symlink_to(self.root / 'inside.md')
        errors = check_links(self.root)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any('escapes repository' in error for error in errors))
        self.assertTrue(any('symlink' in error for error in errors))

    def test_git_directory_is_ignored(self) -> None:
        self.write('.git/notes.md', '[missing](none.md)')
        self.assertEqual(check_links(self.root), [])


if __name__ == '__main__':
    unittest.main()
