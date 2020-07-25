#!/usr/bin/python

# Copyright (c) 2011 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Dart frog buildbot steps

Runs tests for the frog compiler (running on the vm or the self-hosting version)
"""

import os
import re
import shutil
import subprocess
import sys

BUILDER_NAME = 'BUILDBOT_BUILDERNAME'

DART_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DART2JS_BUILDER = (
    r'dart2js-(linux|mac|windows)-(debug|release)(-([a-z]+))?-?(\d*)-?(\d*)')
FROG_BUILDER = r'(frog|frogsh)-(linux|mac|windows)-(debug|release)'
WEB_BUILDER = r'web-(ie|ff|safari|chrome|opera)-(win7|win8|mac|linux)(-(\d+))?'

NO_COLOR_ENV = dict(os.environ)
NO_COLOR_ENV['TERM'] = 'nocolor'

def GetBuildInfo():
  """Returns a tuple (compiler, runtime, mode, system, option) where:
    - compiler: 'dart2js', 'frog', 'frogsh', or None when the builder has an
      incorrect name
    - runtime: 'd8', 'ie', 'ff', 'safari', 'chrome', 'opera'
    - mode: 'debug' or 'release'
    - system: 'linux', 'mac', or 'win7'
    - option: 'checked'
  """
  compiler = None
  runtime = None
  mode = None
  system = None
  builder_name = os.environ.get(BUILDER_NAME)
  option = None
  shard_index = None
  total_shards = None
  if builder_name:

    dart2js_pattern = re.match(DART2JS_BUILDER, builder_name)
    frog_pattern = re.match(FROG_BUILDER, builder_name)
    web_pattern = re.match(WEB_BUILDER, builder_name)

    if dart2js_pattern:
      compiler = 'dart2js'
      runtime = 'd8'
      system = dart2js_pattern.group(1)
      mode = dart2js_pattern.group(2)
      option = dart2js_pattern.group(4)
      shard_index = dart2js_pattern.group(5)
      total_shards = dart2js_pattern.group(6)

    elif frog_pattern:
      compiler = frog_pattern.group(1)
      runtime = 'd8'
      system = frog_pattern.group(2)
      mode = frog_pattern.group(3)

    elif web_pattern:
      compiler = 'frog'
      runtime = web_pattern.group(1)
      mode = 'release'
      system = web_pattern.group(2)

      # TODO(jmesserly): do we want to do anything different for the second IE
      # bot? For now we're using it to track down flakiness.
      number = web_pattern.group(4)

  if system == 'windows':
    system = 'win7'

  return (compiler, runtime, mode, system, option, shard_index, total_shards)


def NeedsXterm(compiler, runtime):
  return compiler == 'frogsh' or runtime in ['ie', 'chrome', 'safari', 'opera',
      'ff', 'drt']

def TestStep(name, mode, system, compiler, runtime, targets, flags):
  print '@@@BUILD_STEP %s %s tests: %s %s@@@' % (name, compiler, runtime,
      ' '.join(flags))
  sys.stdout.flush()
  if NeedsXterm(compiler, runtime) and system == 'linux':
    cmd = ['xvfb-run', '-a']
  else:
    cmd = []

  user_test = os.environ.get('USER_TEST', 'no')

  cmd.extend([sys.executable,
              os.path.join(os.curdir, 'tools', 'test.py'),
              '--mode=' + mode,
              '--compiler=' + compiler,
              '--runtime=' + runtime,
              '--time',
              '--report'])

  if user_test == 'yes':
    cmd.append('--progress=color')
  else:
    cmd.extend(['--progress=buildbot', '-v'])

  if flags:
    cmd.extend(flags)
  cmd.extend(targets)

  print 'running %s' % (' '.join(cmd))
  exit_code = subprocess.call(cmd, env=NO_COLOR_ENV)
  if exit_code != 0:
    print '@@@STEP_FAILURE@@@'
  return exit_code


def BuildFrog(compiler, mode, system):
  """ build frog.
   Args:
     - compiler: either 'dart2js', 'frog', 'frogsh' (frog self-hosted)
     - mode: either 'debug' or 'release'
     - system: either 'linux', 'mac', or 'win7'
  """

  os.chdir(DART_PATH)

  print '@@@BUILD_STEP build frog@@@'

  args = [sys.executable, './tools/build.py', '--mode=' + mode, 'dart2js']
  print 'running %s' % (' '.join(args))
  return subprocess.call(args, env=NO_COLOR_ENV)


def TestFrog(compiler, runtime, mode, system, option, flags):
  """ test frog.
   Args:
     - compiler: either 'dart2js', 'frog', or 'frogsh' (frog self-hosted)
     - runtime: either 'd8', or one of the browsers, see GetBuildInfo
     - mode: either 'debug' or 'release'
     - system: either 'linux', 'mac', or 'win7'
     - option: 'checked'
     - flags: extra flags to pass to test.dart
  """

  # Make sure we are in the frog directory
  os.chdir(DART_PATH)

  if compiler == 'dart2js':
    if (option == 'checked'):
      flags.append('--host-checked')
    # Leg isn't self-hosted (yet) so we run the leg unit tests on the VM.
    TestStep("dart2js_unit", mode, system, 'none', 'vm', ['leg'], ['--checked'])

    extra_suites = ['leg_only', 'frog_native']
    TestStep("dart2js_extra", mode, system, 'dart2js', runtime, extra_suites,
        flags)

    TestStep("dart2js", mode, system, 'dart2js', runtime, [], flags)

  elif runtime == 'd8' and compiler in ['frog', 'frogsh']:
    TestStep("frog", mode, system, compiler, runtime, [], flags)
    TestStep("frog_extra", mode, system, compiler, runtime,
        ['frog', 'frog_native', 'peg', 'css'], flags)
    TestStep("sdk", mode, system, 'none', 'vm', ['dartdoc'], flags)

  else:
    tests = ['client', 'language', 'corelib', 'isolate', 'frog',
             'frog_native', 'peg', 'css']

    # TODO(efortuna): Move Mac back to DumpRenderTree when we have a more stable
    # solution for DRT. Right now DRT is flakier than regular Chrome for the
    # isolate tests, so we're switching to use Chrome in the short term.
    if runtime == 'chrome' and system == 'linux':
      TestStep('browser', mode, system, 'frog', 'drt', tests, flags)
      TestStep('browser_dart2js', mode, system, 'dart2js', 'drt', [], flags)
      TestStep('browser_dart2js_extra', mode, system, 'dart2js', 'drt',
               ['leg_only', 'frog_native'], flags)
    else:
      additional_flags = []
      if system.startswith('win') and runtime == 'ie':
        # There should not be more than one InternetExplorerDriver instance
        # running at a time. For details, see
        # http://code.google.com/p/selenium/wiki/InternetExplorerDriver.
        additional_flags += ['-j1']
      TestStep(runtime, mode, system, compiler, runtime, tests,
          flags + additional_flags)

  return 0

def _DeleteFirefoxProfiles(directory):
  """Find all the firefox profiles in a particular directory and delete them."""
  for f in os.listdir(directory):
    item = os.path.join(directory, f)
    if os.path.isdir(item) and f.startswith('tmp'):
      subprocess.Popen('rm -rf %s' % item, shell=True)

def CleanUpTemporaryFiles(system, browser):
  """For some browser (selenium) tests, the browser creates a temporary profile
  on each browser session start. On Windows, generally these files are
  automatically deleted when all python processes complete. However, since our
  buildbot subordinate script also runs on python, we never get the opportunity to
  clear out the temp files, so we do so explicitly here. Our batch browser
  testing will make this problem occur much less frequently, but will still
  happen eventually unless we do this.

  This problem also occurs with batch tests in Firefox. For some reason selenium
  automatically deletes the temporary profiles for Firefox for one browser,
  but not multiple ones when we have many open batch tasks running. This
  behavior has not been reproduced outside of the buildbots.

  Args:
     - system: either 'linux', 'mac', or 'win7'
     - browser: one of the browsers, see GetBuildInfo
  """
  if system == 'win7':
    shutil.rmtree('C:\\Users\\chrome-bot\\AppData\\Local\\Temp',
        ignore_errors=True)
  elif browser == 'ff':
    # Note: the buildbots run as root, so we can do this without requiring a
    # password. The command won't actually work on regular machines without
    # root permissions.
    _DeleteFirefoxProfiles('/tmp')
    _DeleteFirefoxProfiles('/var/tmp')

def main():
  if len(sys.argv) == 0:
    print 'Script pathname not known, giving up.'
    return 1

  compiler, runtime, mode, system, option, shard_index, total_shards = (
      GetBuildInfo())
  shard_description = ""
  if shard_index:
    shard_description = " shard %s of %s" % (shard_index, total_shards)
  print "compiler: %s, runtime: %s mode: %s, system: %s, option: %s%s" % (
      compiler, runtime, mode, system, option, shard_description)
  if compiler is None:
    return 1

  status = BuildFrog(compiler, mode, system)
  if status != 0:
    print '@@@STEP_FAILURE@@@'
    return status
  test_flags = []
  if shard_index:
    test_flags = ['--shards=%s' % total_shards, '--shard=%s' % shard_index]
  if compiler == 'dart2js':
    status = TestFrog(compiler, runtime, mode, system, option, test_flags)
    if status != 0:
      print '@@@STEP_FAILURE@@@'
    return status # Return unconditionally for dart2js.

  if runtime == 'd8' or (system == 'linux' and runtime == 'chrome'):
    status = TestFrog(compiler, runtime, mode, system, option, test_flags)
    if status != 0:
      print '@@@STEP_FAILURE@@@'
      return status

  status = TestFrog(compiler, runtime, mode, system, option,
                    test_flags + ['--checked'])
  if status != 0:
    print '@@@STEP_FAILURE@@@'

  if compiler == 'frog' and runtime in ['ff', 'chrome', 'safari', 'opera',
      'ie', 'drt']:
    CleanUpTemporaryFiles(system, runtime)
  return status


if __name__ == '__main__':
  sys.exit(main())
