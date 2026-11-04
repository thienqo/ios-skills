# Toolbars, Navigation Bars, and Tabs: iOS 27 Updates

## Contents

- [Navigation bar minimization](#navigation-bar-minimization)
- [Overflow and priority](#overflow-and-priority)
- [TabView](#tabview)
- [Status bar](#status-bar)
- [Pickers and sheets](#pickers-and-sheets)
- [UIKit equivalents](#uikit-equivalents)
- [Sources](#sources)

## Navigation bar minimization

`toolbarMinimizationBehavior(_:for:)` (iOS 27.0+) minimizes the navigation bar. It replaces `toolbarMinimizeBehavior`.

```swift
NavigationStack {
    ScrollView { /* content */ }
        .navigationTitle("Minimizing Title")
        .toolbarMinimizationBehavior(.onScrollDown, for: .navigationBar)
}
```

`ToolbarMinimizationBehavior` cases: `automatic` (system decides; iOS minimizes navigation bars by default when the view has a searchable element), `never`, `onScrollDown`, `onScrollUp`.

- An integrated top tab bar minimizes together with the navigation bar.
- The safe area adjusts by default; customize with `toolbarMinimizationSafeAreaAdjustment(_:for:)`.
- Related: `toolbarMinimizationRestoration(_:for:)`.
- `tabBarMinimizeBehavior(_:)` (iOS 26, iPhone only) is still documented without a deprecation notice; keep it for bottom tab bars.

## Overflow and priority

- `ToolbarOverflowMenu` (iOS/iPadOS/Mac Catalyst/visionOS 27.0+) always places its actions in the overflow menu, regardless of toolbar mode, platform, or customization.
- `visibilityPriority` and the `topBarPinnedTrailing` placement control which items stay visible when space runs out. Verify exact signatures in the 27 SDK before use.

```swift
ContentView()
    .toolbar {
        ToolbarOverflowMenu {
            Button("Action 1") { }
            Button("Action 2") { }
        }
    }
```

## TabView

- Selection must now be a visible tab. A selection pointing at a hidden tab is enforced against.
- `prominent` tab role (iOS 27) for a visually emphasized tab.

## Status bar

- `toolbarColorScheme(_:for: .statusBar)` sets the status bar color scheme.
- `toolbarVisibility(_:for: .statusBar)` hides it conditionally.

## Pickers and sheets

- `TabsPickerStyle` (`.tabs`): tab-style picker; VoiceOver announces it as "tabs".
- `crossFade` sheet transition.

## UIKit equivalents

`UINavigationItem.navigationBarMinimization` replaces `barMinimizeBehavior` and `barMinimizationSafeAreaAdjustment`. `UISearchController` center placement shows the scope bar inline with the search field.

## Sources

- https://sosumi.ai/documentation/swiftui/view/toolbarminimizationbehavior(_:for:)
- https://sosumi.ai/documentation/swiftui/toolbarminimizationbehavior
- https://sosumi.ai/documentation/swiftui/toolbaroverflowmenu
- https://sosumi.ai/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes
- https://sosumi.ai/documentation/updates/swiftui
