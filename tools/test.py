#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 roolrz
# SPDX-License-Identifier: Apache-2.0

"""Run documentation tests in an isolated, requirements-owned environment."""

import hashlib
import os
from pathlib import Path
import subprocess
import sys
import venv

root = Path(__file__).resolve().parents[1]
output = Path(os.environ.get('HYPER_BUILD_OUTPUT', os.environ.get('OUT', root / 'out')))
environment = output / 'build/docs-tests/venv'
requirements = root / 'tools/requirements.txt'
identity = hashlib.sha256(requirements.read_bytes() + sys.version.encode()).hexdigest()
python = environment / 'bin/python'
stamp = environment / 'requirements.sha256'
if not python.is_file():
    venv.EnvBuilder(with_pip=True).create(environment)
if not stamp.is_file() or stamp.read_text() != identity:
    subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check',
                    '-r', str(requirements)], check=True)
    stamp.write_text(identity)
subprocess.run([str(python), '-B', '-m', 'unittest', 'discover', '-s', str(root / 'tools'),
                '-p', 'test_*.py'], check=True)
