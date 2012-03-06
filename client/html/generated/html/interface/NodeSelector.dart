// Copyright (c) 2011, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

// WARNING: Do not edit - generated code.

interface NodeSelector {

  // TODO(nweiz): add this back once DocumentFragment is ported. 
  // ElementList queryAll(String selectors);


  Element query(String selectors);

  NodeList _querySelectorAll(String selectors);

}
