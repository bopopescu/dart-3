
class _SVGFEOffsetElementImpl extends _SVGElementImpl implements SVGFEOffsetElement native "*SVGFEOffsetElement" {

  final _SVGAnimatedNumberImpl dx;

  final _SVGAnimatedNumberImpl dy;

  final _SVGAnimatedStringImpl in1;

  // From SVGFilterPrimitiveStandardAttributes

  final _SVGAnimatedLengthImpl height;

  final _SVGAnimatedStringImpl result;

  final _SVGAnimatedLengthImpl width;

  final _SVGAnimatedLengthImpl x;

  final _SVGAnimatedLengthImpl y;

  // From SVGStylable

  _SVGAnimatedStringImpl get _className() native "return this.className;";

  // Use implementation from Element.
  // final _CSSStyleDeclarationImpl style;

  _CSSValueImpl getPresentationAttribute(String name) native;
}