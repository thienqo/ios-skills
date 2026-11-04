# SwiftUI Patterns: iOS 27 Updates

Changes in the iOS 27 / Xcode 27 SDK that affect state, previews, documents, and common views. Gate with `#available` unless the note says it back-deploys.

## Contents

- [State macro](#state-macro)
- [ContentBuilder](#contentbuilder)
- [Previews](#previews)
- [Documents](#documents)
- [Views and modifiers](#views-and-modifiers)
- [Deprecations](#deprecations)
- [Sources](#sources)

## State macro

Building with Xcode 27 swaps the `@State` property wrapper for the `State()` macro. Declarations keep the same syntax. Per the iOS 27 release notes it avoids re-evaluating the initial value and back-deploys to iOS 17-aligned OSes. Xcode 26 and earlier still use the property wrapper.

Source-breaking cases when moving to Xcode 27:

- An initializer assignment combined with a declaration-site value no longer compiles.
- The synthesized private memberwise init is disabled in extensions.
- Composing `@State` with other property wrappers or macros is unsupported.

```swift
struct CounterView: View {
    @State private var count = 0          // OK

    // Breaks on Xcode 27: declaration-site value plus init assignment
    // @State private var count = 0
    // init(count: Int) { _count = State(initialValue: count) }
}
```

Keep `@State` `private`, keep defaults cheap and side-effect free (SwiftUI re-creates the default when it instantiates the view), and use `.task` for deferred setup.

## ContentBuilder

`ContentBuilder` is a type alias for `ViewBuilder`, positioned as the single builder for views, toolbar content, and commands.

```swift
@ContentBuilder
var editingToolbarItems: some ToolbarContent {
    ForEach(EditingOptions.toolbarItems, id: \.self) { option in
        ToolbarItem { Button(option.title) { option.action() } }
    }
}
```

Existing `@ViewBuilder` and `@ToolbarContentBuilder` code keeps working.

`@Entry` now warns when the default value is a class instance or closure. Keep environment defaults as value types.

## Previews

`PreviewProvider` and its preview modifiers are deprecated in Xcode 27. Use `#Preview`. See [migration-view-lifecycle-layout.md](migration-view-lifecycle-layout.md#previewprovider-to-preview-macro).

## Documents

New protocols for document-based apps with direct disk access:

- `ReadableDocument`, `WritableDocument`: async read/write with progress and the document URL. `read(from:progress:)` and `write(content:to:previous:progress:)` requirements are `@concurrent`.
- `Document`: combines both; use with `DocumentGroup`.
- New `DocumentGroup` initializers plus an `Observable` `URLDocumentConfiguration` for editing-only apps and custom pre-open UI. `URLDocumentConfiguration` is no longer `Sendable`; `makeDocument` and `makeReadableDocument` closures are `@MainActor`.
- `fileExporter(isPresented:documents:contentTypes:onCompletion:onCancellation:)` exports `WritableDocument` collections.
- `FileWrapperDocumentWriter`'s `makeFileWrapper` now receives `previous: FileWrapper?` for incremental package writes; update existing closures.
- `\.newDocument` accepts an in-memory `ReadableDocument` on macOS 27.

`FileDocument` and `ReferenceFileDocument` are deprecated for `DocumentGroup`; prefer `Document` or `ReadableDocument`.

## Views and modifiers

| API | Note |
|---|---|
| `AsyncImage` | Caches via HTTP caching headers. New `URLRequest` initializers with `cachePolicy`; `View.asyncImageURLSession(_:)` sets the session |
| `Text` + `.textSelection(.enabled)` | Uses system selection UI when built with the iOS 27 SDK; works with `TextRenderer` on iOS and macOS |
| `textInputBorderShape(_:)`, `TextInputBorderShape` | Customize text input borders. New `.bordered` text field style; `.squareBorder` and `.roundedBorder` are soft-deprecated |
| `toolbarColorScheme(_:for: .statusBar)`, `toolbarVisibility(_:for: .statusBar)` | Status bar color scheme and visibility |
| `LabeledContent` in `Menu` | Value becomes the menu item subtitle |
| `alert`/`confirmationDialog` with data item or error | Overloads back-deploy |
| Gesture initializers with input sources | Restrict to direct touch, pencil, or pointer |
| `sceneAccessory` with `ExternalNonInteractiveAccessory` | Non-interactive content on external displays |
| `crossFade` sheet transition | New sheet transition |

Menu item symbol images are hidden by default on iPadOS 27 and macOS 27. Restore with `labelStyle(_:)` set to `.titleAndIcon`.

Navigation bars, tabs, and toolbars: [swiftui-navigation](../../swiftui-navigation/SKILL.md). Reordering and drag containers: [swiftui-layout-components](../../swiftui-layout-components/SKILL.md).

## Deprecations

| Deprecated | Use |
|---|---|
| `PreviewProvider` | `#Preview` |
| `FileDocument`, `ReferenceFileDocument` (for `DocumentGroup`) | `Document`, `ReadableDocument` |
| `.squareBorder`, `.roundedBorder` text field styles | `.bordered` |
| `toolbarMinimizeBehavior` | `toolbarMinimizationBehavior` |

## Sources

- https://sosumi.ai/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes
- https://sosumi.ai/documentation/xcode-release-notes/xcode-27-release-notes
- https://sosumi.ai/documentation/swiftui/state
- https://sosumi.ai/documentation/swiftui/contentbuilder
- https://sosumi.ai/documentation/updates/swiftui
