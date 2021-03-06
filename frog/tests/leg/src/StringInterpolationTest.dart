// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

// Test that string interpolations optimize constants, so there are no
// dynamic concatenations.

#import("compiler_helper.dart");

main() {
  String code =
      compileAll(@'''main() { return "${2}${true}${'a'}${3.14}"; }''');

  Expect.isTrue(code.contains(@'2truea3.14'));
}
