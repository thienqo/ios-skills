# Reorderable Containers and Drag Containers (iOS 27)

iOS 27 adds reordering to any list, stack, grid, or custom layout, not only `List` + `onMove`. SwiftUI draws the drag preview, placeholder, and drop animation. Your code applies the change to the model.

## Contents

- [Single collection](#single-collection)
- [Multiple collections](#multiple-collections)
- [Multi-item drag without reordering](#multi-item-drag-without-reordering)
- [Adaptive primary/secondary layout](#adaptive-primarysecondary-layout)
- [Rules](#rules)
- [Sources](#sources)

## Single collection

Mark the `ForEach` with `.reorderable()` and the enclosing container with `reorderContainer(for:isEnabled:move:)`. Use `reorderContainer(for:itemID:isEnabled:move:)` when the model is not `Identifiable` or another property is the ID.

```swift
ScrollView {
    VStack {
        ForEach(cards) { card in
            CardView(card: card)
        }
        .reorderable()
    }
    .reorderContainer(for: Card.self) { difference in
        cards.apply(difference: difference)
    }
}
```

`move` runs once at the end of the reorder session with a `ReorderDifference`:

- `sources`: IDs of moved items, in selection order. Handle all of them, not only `sources[0]`.
- `destination.position`: `.before(id)` or `.end`.

## Multiple collections

Tag each group and name the collection ID type on the container. Signature: `reorderContainer(for:in:isEnabled:move:)`, requires `Item: Identifiable`, `CollectionID: Hashable & Sendable`.

```swift
ForEach(section.cards) { card in
    CardView(card: card)
}
.reorderable(collectionID: section.id)

// On the container
.reorderContainer(for: Card.self, in: Section.ID.self) { difference in
    let destinationSectionID = difference.destination.collectionID
    // remove moved items from their sections, insert at destination.position
}
```

## Multi-item drag without reordering

For drag-out only (copy to another area, export), values must be `Transferable`.

- `draggable(containerItemID:)` on each item
- `dragContainer(for:)` on the grid; closure maps dragged IDs to model values
- `dragContainerSelection(_:)` includes the current selection when one selected item is dragged
- `dropDestination(for:isEnabled:action:)` on the target
- `onDragSessionUpdated(_:)` for phase and location

```swift
LazyVGrid(columns: [GridItem(.adaptive(minimum: 120))]) {
    ForEach(cards) { card in
        CardView(card: card).draggable(containerItemID: card.id)
    }
}
.dragContainer(for: Card.self) { ids in cards.filter { ids.contains($0.id) } }
.dragContainerSelection(selectedIDs)
```

Drag containers do not reorder. Drag container APIs now work on iPhone and iPad.

## Adaptive primary/secondary layout

`ArrangementView` (iOS 27.1+) lays out a primary and secondary view and adapts to size class, orientation, and reserved regions such as a fold or camera. Styles: `.split` (separate spaces) and `.overlay`.

```swift
ArrangementView {
    NowPlayingView()
} secondary: {
    LyricsView()
}
.arrangementViewStyle(.split)
```

Tuning: `.split.axes(.vertical)`, `overlayArrangementEdge(_:)`, `splitArrangementLayoutRatio(_:)`, `splitArrangementFixedLayoutSize(horizontal:vertical:)`, `splitArrangementLayoutSize(...)`. `GeometryProxy` can query `ReservedRegion`s. Gate with `#available(iOS 27.1, *)`.

## Rules

- Gate with `#available(iOS 27, *)`; keep `List` + `onMove` for iOS 26.
- Update the model inside `move`; the view does not mutate the array itself.
- Reordering applies at drag end, not live during the drag.
- `OutlineGroup` does not support native reordering yet.
- API shapes come from the iOS 27 SDK docs and WWDC26 session material; recheck against the shipping SDK.

## Sources

- https://sosumi.ai/documentation/swiftui/view/reordercontainer(for:in:isenabled:move:)
- https://sosumi.ai/documentation/swiftui/arrangementview
- https://www.nilcoalescing.com/blog/NewSwiftUIAPIsForReorderingAndDragAndDropOniOS27
