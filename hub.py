#!/usr/bin/env python3
"""User-owned skill hub. Python 3.9+, standard library, macOS/Linux."""
import argparse
import base64
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
BEGIN = '\n<!-- personal-agent-pack:begin -->\n'
END = '\n<!-- personal-agent-pack:end -->\n'


class HubError(Exception):
    pass


def encode(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def digest(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def read(path):
    return path.read_bytes() if path.exists() else None


def safe_path(base, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or str(rel) in ('', '.'):
        raise HubError('不安全的相对路径: ' + str(relative))
    current = base
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise HubError('目标包含符号链接，先人工确认: ' + str(current))
    if current.exists() and not current.is_file():
        raise HubError('预期文件的位置不是普通文件: ' + str(current))
    return current


def atomic_write(path, data, mode=0o600):
    if data is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.hub-', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def snapshot(path):
    data = read(path)
    return {'data': base64.b64encode(data).decode() if data is not None else None,
            'mode': stat.S_IMODE(path.stat().st_mode) if data is not None else 0o600}


def restore(path, snap):
    atomic_write(path, base64.b64decode(snap['data']) if snap['data'] is not None else None,
                 snap['mode'])


class Package:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.manifest = json.loads((self.root / 'manifest.json').read_text())
        self.id = self.manifest['id']
        if self.id != 'personal-agent-pack' or self.manifest.get('schema_version') != 1:
            raise HubError('不支持的包标识或 schema_version')
        self.resources = json.loads((self.root / 'navigation/resources.json').read_text())
        self.files = {name: (self.root / name).read_bytes() for name in ('manifest.json', 'hub.py')}
        for folder in ('profile', 'preferences', 'navigation', 'skills', 'adapters'):
            for p in sorted((self.root / folder).rglob('*')):
                if p.is_symlink():
                    raise HubError('主库内容不能包含外部符号链接: ' + str(p))
                if p.is_file():
                    self.files[p.relative_to(self.root).as_posix()] = p.read_bytes()
        self.revision = digest(b''.join(name.encode() + b'\0' + self.files[name] + b'\0'
                                       for name in sorted(self.files)))
        names = set()
        for skill in self.manifest['skills']:
            name = skill['name']
            if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
                raise HubError('技能名称无效或重复: ' + name)
            names.add(name)
            body = self.files.get('skills/' + name + '/SKILL.md', b'').decode()
            if not body.startswith('---\n') or '\nname: ' + name + '\n' not in body:
                raise HubError('技能缺失或 frontmatter 名称不一致: ' + name)
            if '\ndescription: ' not in body or '[TODO' in body:
                raise HubError('技能缺少 description 或含占位内容: ' + name)
            for resource in skill['resources']:
                if resource not in self.resources:
                    raise HubError('导航不存在: ' + resource)
        discovered = {Path(k).parts[1] for k in self.files
                      if k.startswith('skills/') and k.endswith('/SKILL.md')}
        if discovered != names:
            raise HubError('技能目录与 manifest 技能清单不一致')

    def skill_files(self):
        files = {k: v for k, v in self.files.items() if k.startswith('skills/')}
        for skill in self.manifest['skills']:
            prefix = 'skills/' + skill['name'] + '/references/'
            files[prefix + 'resources.json'] = encode({
                'hub_version': self.manifest['version'], 'revision': self.revision,
                'timezone': self.manifest['timezone'],
                'resources': {key: self.resources[key] for key in skill['resources']}})
            files[prefix + 'connection.md'] = self.files['adapters/connection.md']
            if skill['name'] == 'personal-article-writing':
                files[prefix + 'writing.md'] = self.files['preferences/writing.md']
        return files

    def entry(self, skill_root):
        def inline(name):
            return (self.files[name].decode().strip()
                    .replace('navigation/provenance.md', str(self.root / 'navigation/provenance.md'))
                    .replace('本目录的 writing.md', str(skill_root / 'personal-article-writing/references/writing.md')))
        lines = [BEGIN.rstrip('\n'), '# 个人 Skill Hub · ' + self.manifest['version'],
                 '内容版本: ' + self.revision[:12],
                 '主库原件: ' + str(self.root),
                 '以下为用户默认设置；当前明确要求和宿主的权限规则优先。',
                 inline('profile/about.md'),
                 inline('preferences/core.md'),
                 '## 按需工作流',
                 '以下路径为已安装技能；按当前任务读取相关 SKILL.md 及其 references/resources.json。']
        lines.extend('- ' + s['title'] + ': ' + str(skill_root / s['name'] / 'SKILL.md')
                     for s in self.manifest['skills'])
        lines.extend(['## 更新主库',
                      '用户明确要求记住偏好、个人信息或修改工作流时，编辑主库四部分中的相应原件。',
                      '先查看原文和来源，保留适用范围；推测不自动升级为个人事实。',
                      '具体任务记录留在导航指向的系统。不要修改已生成技能副本作为主版本。',
                      '修改后运行主库 hub.py validate，再对已接入的客户端运行 hub.py update <agent>。',
                      '报告实际同步到的客户端；目标不可写或发生冲突时保留主库修改并说明未同步。',
                      '只迁移技能不会自动迁移账户授权、自动化或会话访问权限。'])
        return '\n'.join(lines) + END


def block(text):
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise HubError('全局入口标记损坏或重复；未修改文件')
    if BEGIN not in text:
        if 'personal-agent-pack:begin' in text or 'personal-agent-pack:end' in text:
            raise HubError('发现不完整 Hub 标记；未修改文件')
        return None
    first, last = text.index(BEGIN), text.index(END)
    if last < first:
        raise HubError('全局入口标记顺序错误')
    return text[first:last + len(END)]


def locations(home, agent, package, state=None):
    instruction = '.codex/AGENTS.md' if agent == 'codex' else '.claude/CLAUDE.md'
    if state:
        skill_root = state['skill_root']
    elif agent == 'claude':
        skill_root = '.claude/skills'
    else:
        # Preserve the user's working legacy skills instead of creating duplicates.
        legacy = home / '.codex/skills'
        skill_root = '.codex/skills' if any((legacy / s['name']).exists()
                                           for s in package.manifest['skills']) else '.agents/skills'
    if agent == 'codex':
        other = '.agents/skills' if skill_root == '.codex/skills' else '.codex/skills'
        duplicates = [s['name'] for s in package.manifest['skills']
                      if (home / other / s['name']).exists()]
        if duplicates:
            raise HubError('另一个 Codex 技能目录已有同名技能，先处理重复: ' + ', '.join(duplicates))
    return instruction, skill_root


def state_file(home, agent):
    return safe_path(home, '.agentpack/' + agent + '/state.json')


def load_state(home, agent):
    p = state_file(home, agent)
    state = json.loads(p.read_text()) if p.exists() else None
    if state and (state.get('id') != 'personal-agent-pack' or state.get('schema_version') != 1):
        raise HubError('安装记录格式不匹配')
    return state


@contextlib.contextmanager
def lock(home, agent):
    p = safe_path(home, '.agentpack/' + agent + '/operation.lock')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise HubError('已有接入操作正在进行')
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def desired(package, home, agent, state):
    instruction, skill_root = locations(home, agent, package, state)
    files = {skill_root + '/' + k[len('skills/'):]: v for k, v in package.skill_files().items()}
    newblock = package.entry(home / skill_root)
    p = safe_path(home, instruction)
    text = (read(p) or b'').decode()
    oldblock = block(text)
    if state:
        if oldblock != state['block']:
            raise HubError('全局入口内有本地修改或被移除；请先合并到主库')
        text = text.replace(oldblock, newblock, 1)
    elif oldblock:
        raise HubError('已有 Hub 入口但缺少安装记录；不能自动接管')
    else:
        text += newblock
    files[instruction] = text.encode()
    return files, instruction, skill_root, newblock


def prepare(package, home, agent, adopt=False, uninstall=False):
    state = load_state(home, agent)
    if uninstall and not state:
        raise HubError('该客户端尚未接入')
    files, instruction, skill_root, newblock = desired(package, home, agent, state)
    managed = state['files'] if state else {}
    for rel, info in managed.items():
        if rel == instruction:
            continue
        if digest(read(safe_path(home, rel))) != info['sha256']:
            raise HubError('已安装文件有本地修改或丢失，请先合并: ' + rel)
    if uninstall:
        files = {}
        for rel, info in managed.items():
            if rel != instruction:
                original = info['original']
                files[rel] = base64.b64decode(original['data']) if original['data'] is not None else None
        p = safe_path(home, instruction)
        text = p.read_text().replace(state['block'], '', 1)
        original = managed[instruction]['original']
        files[instruction] = None if text == '' and original['data'] is None else text.encode()
    else:
        for rel in set(managed) - set(files):
            original = managed[rel]['original']
            files[rel] = base64.b64decode(original['data']) if original['data'] is not None else None
        conflicts = [rel for rel in files if rel != instruction and rel not in managed
                     and read(safe_path(home, rel)) is not None]
        if conflicts and not adopt:
            raise HubError('已有同名文件，预览后用 --adopt-existing 备份接管: ' + ', '.join(conflicts))
    changes = {rel: data for rel, data in files.items() if read(safe_path(home, rel)) != data}
    return state, files, changes, instruction, skill_root, newblock


def install(package, home, agent, adopt=False, dry_run=False, uninstall=False):
    def operation():
        state, files, changes, instruction, skill_root, newblock = prepare(
            package, home, agent, adopt, uninstall)
        summary = {'agent': agent, 'action': 'uninstall' if uninstall else 'install/update',
                   'dry_run': dry_run, 'version': package.manifest['version'],
                   'revision': package.revision[:12], 'skill_root': str(home / skill_root),
                   'changed_files': list(changes), 'count': len(changes)}
        if dry_run:
            return summary
        previous = {rel: snapshot(safe_path(home, rel)) for rel in changes}
        sp = state_file(home, agent)
        old_state = snapshot(sp)
        new_state = None
        if not uninstall:
            tracked = {}
            _, current_skills = locations(home, agent, package, state)
            wanted = {current_skills + '/' + k[len('skills/'):] for k in package.skill_files()}
            wanted.add(instruction)
            for rel in wanted:
                original = (state['files'][rel]['original'] if state and rel in state['files']
                            else snapshot(safe_path(home, rel)))
                tracked[rel] = {'sha256': digest(files[rel]), 'original': original}
            new_state = {'schema_version': 1, 'id': package.id, 'source': str(package.root),
                         'version': package.manifest['version'], 'revision': package.revision,
                         'skill_root': skill_root, 'instruction': instruction, 'block': newblock,
                         'files': tracked}
        if not changes and state == new_state:
            summary['result'] = 'already_current'
            return summary
        stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
        bp = safe_path(home, '.agentpack/' + agent + '/backups/' + stamp + '.json')
        atomic_write(bp, encode({'agent': agent, 'before': previous, 'state_before': old_state,
                               'instruction': instruction, 'operation': summary['action']}))
        changed = []
        try:
            for rel, data in changes.items():
                p = safe_path(home, rel)
                if snapshot(p) != previous[rel]:
                    raise HubError('操作期间文件发生变化: ' + rel)
                mode = previous[rel]['mode']
                if uninstall and state and rel in state['files']:
                    mode = state['files'][rel]['original']['mode']
                changed.append(rel)
                atomic_write(p, data, mode)
            atomic_write(sp, encode(new_state) if new_state else None)
        except BaseException:
            for rel in reversed(changed):
                restore(safe_path(home, rel), previous[rel])
            restore(sp, old_state)
            raise
        summary.update(result='removed' if uninstall else 'installed', backup=str(bp),
                       pickup='重新开始目标客户端的新会话；当前已加载上下文不保证热更新。')
        return summary
    if dry_run:
        return operation()
    with lock(home, agent):
        return operation()


def status(package, home, agent):
    state = load_state(home, agent)
    if not state:
        return {'agent': agent, 'status': 'not_installed', 'connections': 'not_probed'}
    modified = []
    for rel, info in state['files'].items():
        data = read(safe_path(home, rel))
        if rel == state['instruction']:
            if block((data or b'').decode()) != state['block']:
                modified.append(rel)
        elif digest(data) != info['sha256']:
            modified.append(rel)
    locations(home, agent, package, state)
    return {'agent': agent, 'status': 'modified' if modified else (
            'current' if state['revision'] == package.revision and state['source'] == str(package.root)
            else 'update_available'), 'version': state['version'], 'revision': state['revision'][:12],
            'source': state['source'], 'instruction': str(home / state['instruction']),
            'modified_files': modified, 'connections': 'not_probed',
            'required_capabilities': sorted({c for s in package.manifest['skills'] for c in s['requires']}),
            'note': '文件检查不证明模型已加载，也不证明外部账户授权可用。'}


def export(package, parent):
    out = Path(parent).expanduser().resolve() / package.id
    out.mkdir(parents=True, exist_ok=True)
    files = package.skill_files()
    files.update({k: v for k, v in package.files.items()
                  if k.startswith(('profile/', 'preferences/', 'navigation/'))})
    plugin = json.loads(package.files['adapters/plugin-manifest.json'])
    plugin['version'] = package.manifest['version']
    files['.codex-plugin/plugin.json'] = encode(plugin)
    files['.claude-plugin/plugin.json'] = encode({k: plugin[k] for k in ('name','version','description','author')})
    files['plugin.json'] = encode({'$schema': 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        **{k: plugin[k] for k in ('name','version','description','author')}})
    files['START-HERE.md'] = ('# 个人 Skill Hub 导出包\n\n' +
        '技能包只负责工作流。常驻个人信息和偏好还需要用户级入口；完整自动接入请使用主库 hub.py install。\n'+
        '本导出包不注册 marketplace、不创建调度、不携带账户凭据。不要同时用原生接入与插件安装同一套技能。\n'+
        '个人信息见 profile/about.md；偏好见 preferences/core.md；导航见 navigation/resources.json。\n').encode()
    record = safe_path(out, '.hub-export.json')
    old = json.loads(record.read_text()) if record.exists() else {'files': {}}
    if old.get('id', package.id) != package.id:
        raise HubError('导出目录属于其他包')
    for rel, sha in old['files'].items():
        if digest(read(safe_path(out, rel))) != sha:
            raise HubError('导出副本有本地修改，请先保留: ' + rel)
    for rel in files:
        if rel not in old['files'] and read(safe_path(out, rel)) is not None:
            raise HubError('导出目录有未接管的同名文件: ' + rel)
    for rel in set(old['files']) - set(files):
        atomic_write(safe_path(out, rel), None)
    for rel, data in files.items():
        atomic_write(safe_path(out, rel), data)
    atomic_write(record, encode({'id': package.id, 'revision': package.revision,
                                'files': {k: digest(v) for k, v in files.items()}}))
    return {'output': str(out), 'skills': len(package.manifest['skills']), 'revision': package.revision[:12]}


def main():
    parser = argparse.ArgumentParser(description='个人 Skill Hub：接入、更新、检查、导出和撤销')
    parser.add_argument('--source', type=Path, default=ROOT)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('list')
    sub.add_parser('menu')
    p = sub.add_parser('export'); p.add_argument('--output', type=Path, default=ROOT / 'exports')
    for cmd in ('install', 'update', 'check', 'uninstall'):
        p = sub.add_parser(cmd)
        p.add_argument('agent', choices=('codex', 'claude'))
        p.add_argument('--home', type=Path, default=Path.home(), help='目标用户目录；测试时使用空目录')
        if cmd != 'check':
            p.add_argument('--dry-run', action='store_true')
        if cmd in ('install', 'update'):
            p.add_argument('--adopt-existing', action='store_true', help='备份并接管首次安装遇到的同名技能文件')
    args = parser.parse_args()
    try:
        package = Package(args.source)
        if args.command == 'validate':
            result = {'valid': True, 'version': package.manifest['version'],
                      'revision': package.revision[:12], 'skills': len(package.manifest['skills'])}
        elif args.command == 'list':
            result = package.manifest['skills']
        elif args.command == 'menu':
            return menu(args.source)
        elif args.command == 'export':
            result = export(package, args.output)
        elif args.command == 'check':
            result = status(package, args.home.expanduser().resolve(), args.agent)
        else:
            home = args.home.expanduser().resolve()
            if args.command == 'update' and not load_state(home, args.agent):
                raise HubError('尚未接入，请先 install')
            result = install(package, home, args.agent, getattr(args, 'adopt_existing', False),
                             args.dry_run, args.command == 'uninstall')
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'check' and result['status'] != 'current':
            return 1
        return 0
    except (HubError, OSError, ValueError, KeyError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


def menu(source):
    labels = {'current': '已同步', 'modified': '安装副本有改动，请先合并',
              'update_available': '有待同步更新', 'not_installed': '尚未接入'}
    while True:
        print('\n个人 Skill Hub\n1. 检查接入状态\n2. 同步到已接入的 agent\n3. 导出插件包\n4. 查看工作流\n0. 退出')
        try:
            choice = input('请选择：').strip()
            if choice == '0':
                return 0
            package = Package(source)
            if choice == '1':
                for agent in ('codex', 'claude'):
                    s = status(package, Path.home(), agent)
                    print(agent + '：' + labels[s['status']])
                print('此处检查文件；外部账户连接由目标 agent 在使用时核实。')
            elif choice == '2':
                for agent in ('codex', 'claude'):
                    if load_state(Path.home(), agent):
                        r = install(package, Path.home(), agent)
                        print(agent + '：同步完成，变更文件 ' + str(r['count']))
                print('请在新会话中使用更新后的规则。')
            elif choice == '3':
                print('已导出：' + export(package, Path(source) / 'exports')['output'])
            elif choice == '4':
                for skill in package.manifest['skills']:
                    print(skill['title'] + ' — ' + skill['name'])
            else:
                print('输入 0 至 4。')
        except (EOFError, KeyboardInterrupt):
            return 0
        except (HubError, OSError, ValueError, KeyError) as exc:
            print('未完成：' + str(exc))


if __name__ == '__main__':
    sys.exit(main())
