---
name: swiftui-liquid-glass
description: "Implement or review SwiftUI Liquid Glass for iOS 26+, including glass effects and containers, controls, toolbars, tab bars, morphing transitions, tinting, scroll edges, background extension, and availability fallbacks. Use when adopting the Liquid Glass visual system."
---

# SwiftUI Liquid Glass

Liquid Glass is the dynamic translucent material introduced across Apple platforms
26. Standard SwiftUI bars and presentations adopt it automatically when built with
the current SDK. Reserve custom glass for functional controls and navigation surfaces,
not general content backgrounds.

See [references/liquid-glass.md](references/liquid-glass.md) for the full API reference with additional examples.

## Contents

- [Workflow](#workflow)
- [Core API Summary](#core-api-summary)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Workflow

Choose the path that matches the request:

### 1. Implement a new feature with Liquid Glass

1. Identify target surfaces (floating controls, custom bars, transient controls).
2. Decide shape, prominence, and whether each element is a real control or static status.
3. Wrap grouped glass elements in a `GlassEffectContainer`.
4. Apply `.glassEffect()` **after** layout and appearance modifiers.
5. Add `.interactive()` only to tappable/focusable elements.
6. Add morphing transitions with `glassEffectID(_:in:)` where the view hierarchy
   changes with animation. Put `glassEffectTransition(_:)` on the inserted or
   removed glass child, not on the always-present container, and choose the style
   using [Morphing & Transitions](#morphing--transitions).
7. Gate with `if #available(iOS 26, *)` and provide a fallback for earlier versions.

### 2. Improve an existing feature with Liquid Glass

1. Find custom control or navigation backgrounds that can be replaced with `.glassEffect()`.
2. Wrap sibling glass elements in `GlassEffectContainer` for blending and performance.
3. Replace custom glass-like buttons with `.buttonStyle(.glass)`, `.buttonStyle(.glassProminent)`, or configurable styles such as `.buttonStyle(.glass(.clear))`. Use `.glass(_:)` when the button needs a specific tint or variant; reserve `.glassProminent` for high-emphasis primary actions.
4. Add morphing transitions where animated insertion/removal occurs.

### 3. Review existing Liquid Glass usage

Trace each effect through content/control ownership, layout order, container scope, interactivity, transitions, availability, accessibility settings, and fallback. Restore the same UI fixture and rerun the checklist after each correction.

## Core API Summary

### glassEffect(_:in:)

Applies Liquid Glass behind a view. Default: `.regular` variant in a `Capsule` shape.

```swift
nonisolated func glassEffect(
    _ glass: Glass = .regular,
    in shape: some Shape = DefaultGlassEffectShape()
) -> some View
```

### Glass struct

| Property / Method | Purpose |
|---|---|
| `.regular` | Standard glass material |
| `.clear` | Clear variant; add dimming/contrast treatment when legibility needs it |
| `.identity` | No visual effect (pass-through) |
| `.tint(_:)` | Add a color tint for prominence |
| `.interactive(_:)` | React to touch and pointer interactions |

Chain them: `.regular.tint(.blue).interactive()`

### GlassEffectContainer

Wraps multiple glass views for shared rendering, blending, and morphing.

```swift
GlassEffectContainer(spacing: 24) {
    // child views with .glassEffect()
}
```

The `spacing` controls when nearby glass shapes begin to blend. Match or exceed
the interior layout spacing so shapes merge during animated transitions but remain
separate at rest.

### Morphing & Transitions

| Modifier | Purpose |
|---|---|
| `glassEffectID(_:in:)` | Stable identity for morphing during view hierarchy changes |
| `glassEffectUnion(id:namespace:)` | Merge multiple views into one glass shape |
| `glassEffectTransition(_:)` | Control how glass appears/disappears |

Transition decision: use `.matchedGeometry` for nearby effects inside the container's
spacing; use `.materialize` for distant insertion/removal or when no geometry match
should occur; use `.identity` only when no transition animation is wanted.

### Button Styles

```swift
Button("Action") { }
    .buttonStyle(.glass)           // standard glass button

Button("Primary") { }
    .buttonStyle(.glassProminent)  // prominent glass button

Button("Media") { }
    .buttonStyle(.glass(.clear))    // configurable variant; verify contrast
```

### Related iOS 26 APIs

| API | Use |
|---|---|
| `scrollEdgeEffectStyle` | Configure a scroll boundary's visual treatment. |
| `backgroundExtensionEffect` | Extend one background under safe-area edges with mirrored blur. |
| `ToolbarSpacer` | Create a visual break between toolbar items. |

See the corresponding sections in
[references/liquid-glass.md](references/liquid-glass.md) for signatures and examples.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Glass decorates static content | Keep it in the controls/navigation layer. |
| Read-only status uses `.interactive()` or an action slot | Present status as content, or make the whole badge one real accessible action. |
| Related effects use nested containers | Use one `GlassEffectContainer` per related blending/morphing group. |
| `.glassEffect()` precedes padding/frame/style | Apply layout and appearance first, then glass. |
| Custom effects assume default accessibility settings | Test Reduce Transparency, Reduce Motion, contrast, and legibility. |
| No pre-iOS 26 path | Gate the effect and preserve a functional fallback. |

## Review Checklist

- [ ] **Availability**: `if #available(iOS 26, *)` present with fallback UI.
- [ ] **Container**: Multiple glass views wrapped in `GlassEffectContainer`.
- [ ] **Modifier order**: `.glassEffect()` applied after layout/appearance modifiers.
- [ ] **Interactivity**: `.interactive()` used only where user interaction exists.
- [ ] **Status vs action**: Static counts/status are not toolbar controls and do not expose press/hover affordance.
- [ ] **Transitions**: `glassEffectID` used with `@Namespace` for morphing animations.
- [ ] **Transition type**: `.matchedGeometry` for nearby effects; `.materialize` for distant ones, applied to the conditional glass child.
- [ ] **Consistency**: Shapes, tints, and spacing are uniform across related elements.
- [ ] **Performance**: Glass effects are limited in number; container used for grouping.
- [ ] **Accessibility**: Tested with Reduce Transparency and Reduce Motion enabled.
- [ ] **Button styles**: Standard `.glass`, `.glassProminent`, or configurable `.glass(_:)` used for buttons; `.glass(_:)` is primary when a tint or clear variant is required.
- [ ] **Clear glass contrast**: Clear glass over bright content has a dimming/contrast treatment or uses a more legible style.
- [ ] **Concurrency**: IDs passed to `glassEffectID` / `glassEffectUnion` are `Sendable`; MainActor-annotated Liquid Glass APIs stay in SwiftUI UI code.

## References

- Full API guide: [references/liquid-glass.md](references/liquid-glass.md)
- Apple docs: [Applying Liquid Glass to custom views](https://sosumi.ai/documentation/swiftui/Applying-Liquid-Glass-to-custom-views)
- Apple docs: [Adopting Liquid Glass](https://sosumi.ai/documentation/technologyoverviews/adopting-liquid-glass)
