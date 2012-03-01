// Copyright (c) 2012, the Dart project authors.  Please see the AUTHORS file
// for details. All rights reserved. Use of this source code is governed by a
// BSD-style license that can be found in the LICENSE file.

class _EventsImpl implements Events {
  /* Raw event target. */
  // TODO(jacobr): it would be nice if we could specify this as
  // _EventTargetImpl or EventTarget
  final var _ptr;

  _EventsImpl(this._ptr);

  _EventListenerListImpl operator [](String type) => _get(type.toLowerCase());
  
  _EventListenerListImpl _get(String type) {
    return new _EventListenerListImpl(_ptr, type);
  }
}

class _EventListenerListImpl implements EventListenerList {
  
  // TODO(jacobr): make this _EventTargetImpl
  final var _ptr;
  final String _type;

  _EventListenerListImpl(this._ptr, this._type);

  // TODO(jacobr): implement equals.

  _EventListenerListImpl add(EventListener listener,
      [bool useCapture = false]) {
    _add(listener, useCapture);
    return this;
  }

  _EventListenerListImpl remove(EventListener listener,
      [bool useCapture = false]) {
    _remove(listener, useCapture);
    return this;
  }

  bool dispatch(Event evt) {
    // TODO(jacobr): what is the correct behavior here. We could alternately
    // force the event to have the expected type.
    assert(evt.type == _type);
    return _ptr._dispatchEvent(evt);
  }

  void _add(EventListener listener, bool useCapture) {
    _ptr._addEventListener(_type, listener, useCapture);
  }

  void _remove(EventListener listener, bool useCapture) {
    _ptr._removeEventListener(_type, listener, useCapture);
  }
}


class _EventTargetImpl implements EventTarget native "*EventTarget" {

  Events get on() => new _EventsImpl(this);

  void _addEventListener(String type, EventListener listener, [bool useCapture = null]) native "this.addEventListener(type, listener, useCapture);";

  bool _dispatchEvent(_EventImpl event) native "return this.dispatchEvent(event);";

  void _removeEventListener(String type, EventListener listener, [bool useCapture = null]) native "this.removeEventListener(type, listener, useCapture);";

}