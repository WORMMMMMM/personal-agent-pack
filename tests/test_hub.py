import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('hub', SOURCE / 'hub.py')
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


class HubTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='skill hub 测试 ')
        self.base = Path(self.temp.name)
        self.home = self.base / '用户目录'
        self.home.mkdir()
        self.source = self.base / '主库'
        shutil.copytree(SOURCE, self.source, ignore=shutil.ignore_patterns('exports', '.git', '__pycache__'))
        self.package = hub.Package(self.source)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, rel, data):
        p = self.home / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return p

    def test_both_agents_install_idempotent_and_uninstall(self):
        for agent, entry in [('codex', '.codex/AGENTS.md'), ('claude', '.claude/CLAUDE.md')]:
            original = '原有配置，不属于 Hub。\n'.encode()
            p = self.write(entry, original)
            result = hub.install(self.package, self.home, agent)
            self.assertGreater(result['count'], 0)
            self.assertEqual(hub.status(self.package, self.home, agent)['status'], 'current')
            self.assertEqual(hub.install(self.package, self.home, agent)['result'], 'already_current')
            hub.install(self.package, self.home, agent, uninstall=True)
            self.assertEqual(p.read_bytes(), original)
            self.assertEqual(hub.status(self.package, self.home, agent)['status'], 'not_installed')

    def test_adoption_backs_up_and_restores_old_skill(self):
        rel = '.codex/skills/notion-diary-capture/SKILL.md'
        p = self.write(rel, b'original skill')
        p.chmod(0o640)
        with self.assertRaises(hub.HubError):
            hub.install(self.package, self.home, 'codex')
        self.assertEqual(p.read_bytes(), b'original skill')
        result = hub.install(self.package, self.home, 'codex', adopt=True)
        saved = json.loads(Path(result['backup']).read_text())
        self.assertIn(rel, saved['before'])
        hub.install(self.package, self.home, 'codex', uninstall=True)
        self.assertEqual(p.read_bytes(), b'original skill')
        self.assertEqual(p.stat().st_mode & 0o777, 0o640)

    def test_update_preserves_external_global_edits(self):
        hub.install(self.package, self.home, 'claude')
        p = self.home / '.claude/CLAUDE.md'
        p.write_text('新增的独立规则\n' + p.read_text() + '末尾规则\n')
        f = self.source / 'preferences/core.md'
        f.write_text(f.read_text() + '\n- 本次新增偏好。\n')
        newer = hub.Package(self.source)
        self.assertEqual(hub.status(newer, self.home, 'claude')['status'], 'update_available')
        hub.install(newer, self.home, 'claude')
        self.assertIn('本次新增偏好', p.read_text())
        hub.install(newer, self.home, 'claude', uninstall=True)
        self.assertEqual(p.read_text(), '新增的独立规则\n末尾规则\n')

    def test_local_skill_change_blocks_all_update_writes(self):
        hub.install(self.package, self.home, 'claude')
        rel = '.claude/skills/notion-diary-capture/SKILL.md'
        self.write(rel, b'user local edit')
        p = self.home / '.claude/CLAUDE.md'
        before = p.read_bytes()
        self.assertEqual(hub.status(self.package, self.home, 'claude')['status'], 'modified')
        with self.assertRaises(hub.HubError):
            hub.install(self.package, self.home, 'claude', adopt=True)
        self.assertEqual(p.read_bytes(), before)
        self.assertEqual((self.home / rel).read_bytes(), b'user local edit')

    def test_managed_entry_edit_and_bad_markers_rejected(self):
        hub.install(self.package, self.home, 'claude')
        p = self.home / '.claude/CLAUDE.md'
        p.write_text(p.read_text().replace('Sir', 'Captain'))
        with self.assertRaises(hub.HubError):
            hub.install(self.package, self.home, 'claude')
        with self.assertRaises(hub.HubError):
            hub.block(hub.BEGIN + 'broken')

    def test_dry_run_has_no_writes(self):
        before = list(self.home.rglob('*'))
        result = hub.install(self.package, self.home, 'codex', dry_run=True)
        self.assertTrue(result['dry_run'])
        self.assertEqual(list(self.home.rglob('*')), before)

    def test_failed_write_rolls_back(self):
        original = self.write('.claude/CLAUDE.md', b'existing')
        real = hub.atomic_write
        fired = []
        def broken(path, data, mode=0o600):
            if path.name == 'resources.json' and not fired:
                fired.append(True)
                raise OSError('simulated full disk')
            return real(path, data, mode)
        with patch.object(hub, 'atomic_write', broken):
            with self.assertRaises(OSError):
                hub.install(self.package, self.home, 'claude')
        self.assertTrue(fired)
        self.assertEqual(original.read_bytes(), b'existing')
        self.assertIsNone(hub.load_state(self.home, 'claude'))
        self.assertFalse(list((self.home / '.claude/skills').rglob('SKILL.md')))

    def test_symlinks_and_duplicate_codex_roots_rejected(self):
        target = self.base / 'external'; target.mkdir()
        (self.home / '.claude').symlink_to(target, target_is_directory=True)
        with self.assertRaises(hub.HubError):
            hub.install(self.package, self.home, 'claude')
        self.assertEqual(list(target.iterdir()), [])
        self.write('.codex/skills/notion-diary-capture/SKILL.md', b'legacy')
        self.write('.agents/skills/notion-diary-capture/SKILL.md', b'modern')
        with self.assertRaises(hub.HubError):
            hub.install(self.package, self.home, 'codex', adopt=True)

    def test_export_is_self_contained_and_rejects_edited_copy(self):
        result = hub.export(self.package, self.base / '导出')
        out = Path(result['output'])
        self.assertTrue((out / '.codex-plugin/plugin.json').exists())
        self.assertTrue((out / '.claude-plugin/plugin.json').exists())
        for skill in self.package.manifest['skills']:
            p = out / 'skills' / skill['name'] / 'references/resources.json'
            refs = json.loads(p.read_text())
            self.assertEqual(set(refs['resources']), set(skill['resources']))
            self.assertNotIn(str(self.source), p.read_text())
        hub.export(self.package, self.base / '导出')
        p = out / 'skills/notion-diary-capture/SKILL.md'
        p.write_text('manual edit')
        with self.assertRaises(hub.HubError):
            hub.export(self.package, self.base / '导出')

    def test_moved_source_can_update(self):
        hub.install(self.package, self.home, 'claude')
        newpath = self.base / '搬家后的主库'
        self.source.rename(newpath)
        moved = hub.Package(newpath)
        self.assertEqual(hub.status(moved, self.home, 'claude')['status'], 'update_available')
        hub.install(moved, self.home, 'claude')
        self.assertIn(str(newpath), (self.home / '.claude/CLAUDE.md').read_text())

    def test_obsolete_managed_skill_removed_and_unknown_files_kept(self):
        hub.install(self.package, self.home, 'claude')
        self.write('.claude/skills/thinking-field/user-note.txt', b'keep')
        manifest = self.source / 'manifest.json'
        data = json.loads(manifest.read_text())
        data['skills'] = [s for s in data['skills'] if s['name'] != 'thinking-field']
        manifest.write_bytes(hub.encode(data))
        shutil.rmtree(self.source / 'skills/thinking-field')
        newer = hub.Package(self.source)
        hub.install(newer, self.home, 'claude')
        self.assertFalse((self.home / '.claude/skills/thinking-field/SKILL.md').exists())
        self.assertEqual((self.home / '.claude/skills/thinking-field/user-note.txt').read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main(verbosity=2)
