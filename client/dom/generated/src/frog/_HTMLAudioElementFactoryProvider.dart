// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

class _HTMLAudioElementFactoryProvider {
  factory HTMLAudioElement([String src = null]) native
'''
if (src == null) return new Audio();
return new Audio(src);
''';
}