
class _SVGFESpecularLightingElementImpl extends _SVGElementImpl implements SVGFESpecularLightingElement native "*SVGFESpecularLightingElement" {

  final _SVGAnimatedStringImpl in1;

  final _SVGAnimatedNumberImpl specularConstant;

  final _SVGAnimatedNumberImpl specularExponent;

  final _SVGAnimatedNumberImpl surfaceScale;

  // From SVGFilterPrimitiveStandardAttributes

  final _SVGAnimatedLengthImpl height;

  final _SVGAnimatedStringImpl result;

  final _SVGAnimatedLengthImpl width;

  final _SVGAnimatedLengthImpl x;

  final _SVGAnimatedLengthImpl y;

  // From SVGStylable

  _SVGAnimatedStringImpl get _svgClassName() native "return this.className;";

  // Use implementation from Element.
  // final _CSSStyleDeclarationImpl style;

  _CSSValueImpl getPresentationAttribute(String name) native;
}
