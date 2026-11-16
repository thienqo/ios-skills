---
name: focus-engine
description: "Implement or debug keyboard, directional, and scene-level focus across SwiftUI and UIKit. Use for FocusState, focus restoration and routing, tvOS remote navigation, watchOS crown focus, visionOS input focus, macOS key loops, UIFocusGuide, or UIFocusDebugger."
---

# Focus Engine

Focus behavior for SwiftUI and UIKit apps targeting iOS 26+, iPadOS, macOS, tvOS, and visionOS connected-input paths. Covers keyboard focus, directional focus, scene-focused values, focus restoration, and UIKit focus guides. `focusSection()` guidance in this skill applies to macOS and tvOS. visionOS gaze-driven hover is an input affordance, not focus. Accessibility-specific focus for VoiceOver and Switch Control lives in the `ios-accessibility` skill.

When a request mixes focus with accessibility or spatial input, keep the boundary explicit:
- Use this skill for keyboard, remote, game-controller, and scene focus behavior.
- For visionOS, describe gaze, direct touch, and pointer targeting as hover/input affordances, not focus.
- For VoiceOver, Switch Control, Voice Control, or accessibility element ordering, give only a brief handoff to `ios-accessibility`.

## Contents

- [SwiftUI FocusState](#swiftui-focusstate)
- [Default Focus](#default-focus)
- [Focused Values and Scene Values](#focused-values-and-scene-values)
- [Focusable Interactions](#focusable-interactions)
- [Focus Sections](#focus-sections)
- [Focus Restoration](#focus-restoration)
- [UIKit Focus Guides](#uikit-focus-guides)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## SwiftUI FocusState

Use `@FocusState` to read and write focus placement inside a scene. Use `Bool` for a single target or an optional `Hashable` enum for multiple targets. Keep focus state local to the view that owns the focusable controls.

```swift
@FocusState private var focusedField: Field?

TextField("Email", text: $email).focused($focusedField, equals: .email)
.onSubmit { focusedField = .password }
```

See [FocusState patterns](references/focus-patterns.md#focusstate-patterns) for the full multi-field form example.

## Default Focus

Use `.defaultFocus` to set the preferred initial focus region or control when a view appears or when focus is reassigned automatically. Prefer one clear default destination per screen or focus region.

## Focused Values and Scene Values

Use focused values to expose state from the currently focused view. Use scene-focused values (`focusedSceneValue`) when commands or scene-wide UI should keep access to the value even after focus moves within that scene. Use this pattern for menus, commands, and toolbars that need to act on the focused scene's current content.

## Focusable Interactions

Use `.focusable(_:interactions:)` on custom SwiftUI views that should participate in keyboard or directional focus. Prefer semantic `Button`, `Toggle`, `TextField`, and other system controls before making arbitrary gesture-driven views focusable; use `.focusable(interactions: .activate)` for custom button-like controls only when a semantic control cannot express the UI.

## Focus Sections

Use `focusSection()` on macOS 13+ and tvOS 15+ to guide directional movement across groups of focusable descendants in uneven layouts. Use it when default left/right or up/down movement skips the intended group.

## Focus Restoration

After dismissing a sheet, popover, or transient overlay, return focus to a stable trigger or logical next target. Restore focus intentionally whenever presentation changes would otherwise leave users disoriented.

## UIKit Focus Guides

Use `UIFocusGuide` when UIKit or tvOS layouts need custom routing across empty space or awkward geometry. `UIFocusGuide` is invisible and not a view; constrain it like a layout guide and set `preferredFocusEnvironments`. Use it to redirect focus without adding decorative UI.

See [Focus patterns](references/focus-patterns.md) for complete SwiftUI and UIKit examples.

## Common Mistakes

1. Mixing accessibility focus and keyboard or directional focus in the same mental model.
2. Storing `@FocusState` in shared models instead of the owning view.
3. Setting multiple competing default focus targets on one screen.
4. Using `.focusable()` on decorative views.
5. Forgetting focus restoration after sheets, popovers, or custom overlays.
6. Reaching for `UIFocusGuide` before trying `focusSection()` on macOS or tvOS, or better layout grouping in SwiftUI.
7. Using gesture handlers for primary actions on custom focusable controls instead of a semantic `Button` when possible.
8. Treating visionOS gaze hover as focus; reserve focus guidance for connected input such as keyboards and game controllers.

## Review Checklist

- [ ] `@FocusState` is local to the view that owns the controls
- [ ] Initial focus target is explicit when the screen needs one
- [ ] Focus movement between fields or groups is deterministic
- [ ] `focusedSceneValue` or related focused-value APIs are used when commands need current scene state
- [ ] Custom controls opt into focus only when they are truly interactive
- [ ] `focusSection()` is used for uneven directional layouts on macOS or tvOS before dropping to UIKit
- [ ] Focus returns to a stable element after temporary presentations dismiss
- [ ] `UIFocusGuide` geometry and preferred destinations match the intended route
- [ ] visionOS guidance distinguishes connected-device focus from gaze-driven hover or RealityKit input targets
- [ ] Accessibility focus concerns are handled in `ios-accessibility`, not mixed into keyboard-directional focus logic

## References

- Detailed patterns: [references/focus-patterns.md](references/focus-patterns.md)
- Multi-platform focus (tvOS, watchOS, visionOS, macOS): [references/multi-platform-focus.md](references/multi-platform-focus.md)
- Focus debugging and anti-patterns: [references/focus-debugging.md](references/focus-debugging.md)
