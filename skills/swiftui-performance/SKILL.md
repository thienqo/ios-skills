---
name: swiftui-performance
description: "Profiles and fixes SwiftUI runtime performance with code review, Instruments, and repeatable measurement. Use for slow rendering, scrolling or animation hitches, excessive body updates, identity churn, layout spikes, broad Observation invalidation, CPU cost, or before/after verification."
---

# SwiftUI Performance

Audit SwiftUI view performance from a reproducible symptom to measured
remediation. Route animation design to `swiftui-animation`, production telemetry
to `metrickit`, ownership/leak analysis to `ios-memgraph-analysis`, navigation
behavior to `swiftui-navigation`, state architecture to `swiftui-patterns`, and
layout construction to `swiftui-layout-components`.

## Contents

- [Workflow Decision Tree](#workflow-decision-tree)
- [1. Code-First Review](#1-code-first-review)
- [2. Guide the User to Profile](#2-guide-the-user-to-profile)
- [3. Analyze and Diagnose](#3-analyze-and-diagnose)
- [4. Remediate](#4-remediate)
- [Common Code Smells (and Fixes)](#common-code-smells-and-fixes)
- [5. Verify](#5-verify)
- [Outputs](#outputs)
- [Instruments Profiling](#instruments-profiling)
- [Identity and Lifetime](#identity-and-lifetime)
- [Lazy Loading Patterns](#lazy-loading-patterns)
- [State and Observation Optimization](#state-and-observation-optimization)
- [Common Mistakes](#common-mistakes)
- [Review Checklist](#review-checklist)
- [References](#references)

## Workflow Decision Tree

- Code supplied: review it first and label findings as hypotheses.
- Symptoms only: collect the smallest relevant view, data flow, reproduction, device, OS, and build config.
- Inconclusive review: collect a trace or lane screenshots before prescribing a broad refactor.

Use this triage list for both code and trace analysis:

- Broad state dependencies or invalidation storms
- Unstable list identity or root conditional swapping
- Formatting, sorting, decoding, or synchronous I/O in `body`
- Layout/geometry feedback loops and oversized images
- Implicit animation applied to a large hierarchy

## 1. Code-First Review

Map each suspect from the triage list to exact code. Report likely causes with
code references, but label them code-backed hypotheses until a trace confirms
cost. Propose a minimal repro or measurement when evidence is missing.

## 2. Guide the User to Profile

Use the SwiftUI Instruments template on a **Release build** and real device when
possible. Reproduce the exact interaction, capturing SwiftUI lanes, Time
Profiler, and Hangs/Hitches as relevant. Ask for the trace or screenshots of the
lanes and call tree.

## 3. Analyze and Diagnose

Apply the same triage list to trace evidence. Correlate long or frequent SwiftUI
updates with the Time Profiler call tree and the reproduced interaction. Separate
trace-backed findings from code-backed hypotheses and name the next measurement
that would resolve remaining uncertainty.

## 4. Remediate

Apply targeted fixes:
- Narrow state scope (`@State`/`@Observable` closer to leaf views).
- Stabilize identities for `ForEach` and lists.
- Move heavy work out of `body` into model-layer precomputation, an explicit derived
  value updated when its inputs change, a memoized helper, or background processing.
  Use `@State` only when the view owns both the value and its update lifecycle; it is
  not a generic cache for arbitrary computation.
- Use `equatable()` only when equality is cheaper than recomputing the subtree and
  the compared inputs have stable value semantics.
- Downsample images before rendering.
- Reduce layout complexity or use fixed sizing where possible.

## Common Code Smells (and Fixes)

| Smell | Evidence to seek | Targeted fix |
|---|---|---|
| Formatter, sort, filter, or decode in `body` | Long/frequent body updates with matching call-tree cost | Recompute when inputs change; downsample/decode off the main actor |
| `UUID()` or unstable `id: \.self` | Recreated rows, lost state, excess updates | Use stable model identity |
| Root `if`/`else` swaps | State reset or update spikes when toggled | Localize conditional content/modifiers when semantics allow |
| Broad model reads | Many unrelated views update together | Pass narrow values or move reads into focused child views |
| Geometry writes during layout | Repeating layout/update cycle | Threshold changes or replace the feedback path with stable layout |

## 5. Verify

Ask the user to re-run the same capture and compare with baseline metrics.
Summarize the delta (CPU, frame drops, memory peak) if provided.

## Outputs

Provide:
- A short metrics table (before/after if available).
- Top issues (ordered by impact).
- Proposed fixes with estimated effort.

## Instruments Profiling

Use the **SwiftUI template** in Instruments (Cmd+I to profile). Current SwiftUI lanes include Update Groups, Long View Body Updates, Long Representable Updates / Representable Updates, Other Long Updates / Other Updates, and the Cause & Effect Graph. Correlate those with Time Profiler and Hangs/Hitches.

Add `Self._printChanges()` in debug builds to log which property triggered a view update:

```swift
#if DEBUG
let _ = Self._printChanges()  // "MyView: @self, _count changed."
#endif
```

See [references/optimizing-swiftui-performance-instruments.md](references/optimizing-swiftui-performance-instruments.md) for the full profiling workflow.

## Identity and Lifetime

Identity controls view lifetime and state. Use stable model IDs in repeated
content and reserve `.id(_:)` changes for intentional resets. Prefer
`@ViewBuilder` or generic composition over `AnyView` in profiled hot rows. Treat
root conditional branches as suspects—not automatic defects—when evidence shows
state churn or expensive recreation.

```swift
Text(title).foregroundStyle(isHighlighted ? .yellow : .primary)
ForEach(items) { item in Row(item: item).id(item.stableID) }
```

## Lazy Loading Patterns

Use lazy containers when profiling shows eager construction, layout, or update
work is material; there is no universal item-count threshold. Route grid/list
construction choices to `swiftui-layout-components`.

Guardrails:

- Off-screen views are removed from the lazy stack (SwiftUI may keep them briefly), so persist important row state outside the row.
- Body and layout can run before `onAppear` because of prefetching; do not make `onAppear` the only setup point, and treat `onAppear`/`onDisappear` as visibility signals, not lifetime guarantees.
- Filter data before `ForEach`, keep each element to a constant number of top-level subviews, and use `-LogForEachSlowPath YES` while debugging.
- Avoid absolute content-size/offset assumptions; lazy stacks estimate off-screen sizes.
- Avoid geometry feedback loops in lazy rows; prefer stable sizing, a custom `Layout`, or thresholded changes.

## State and Observation Optimization

Observation tracks properties read during view evaluation. Reduce fan-out by
passing narrow derived values or moving reads into focused child views.

```swift
struct ProfileView: View {
    let model: ProfileModel
    var body: some View {
        VStack {
            NameRow(model: model); EmailRow(model: model)          // each tracks only its own reads
            AvatarView(model: model); SettingsForm(model: model)
        }
    }
}
```

Cheap computed values can remain derived; expensive transformations need an
explicit owner, input set, and refresh trigger. Do not add view models as a
performance ritual—measure first and route general state design to
`swiftui-patterns`.

## Common Mistakes

1. **Profiling Debug builds.** Debug builds add runtime checks and disable optimizations; profile Release on a real device.
2. **Observing an entire model when one property is needed.** Split large `@Observable` models or narrow reads with computed properties/closures.
3. **Geometry feedback inside `ScrollView` items.** Prefer stable sizing, custom layout, or thresholded `.onGeometryChange` (iOS 16+).
4. **Creating `DateFormatter`/`NumberFormatter` inside `body`.** Make them static or move them outside the view.
5. **Animating non-equatable state.** Conform to `Equatable` and use `.animation(_:value:)` or `.animation(_:body:)`.
6. **Large flat `List` without identifiers.** Use `id:` or `Identifiable` so SwiftUI diffs instead of rebuilding the entire list.
7. **Unnecessary `@State` wrapper classes.** Use plain `@State` with structs; wrapping a value type in a class defeats value semantics.
8. **Blocking `MainActor` with synchronous I/O.** Move file reads, large parsing, and decoding off the main actor; reserve `Task.detached` for deliberate actor-inheritance breaks.

## Review Checklist

- [ ] No `DateFormatter`/`NumberFormatter` allocations inside `body`
- [ ] Large lists use `Identifiable` items or explicit `id:`
- [ ] `@Observable` models expose only the properties views actually read
- [ ] Heavy computation is off `MainActor` (image processing, parsing)
- [ ] Lazy rows have stable identity, constant top-level row shape, and prefiltered data
- [ ] Geometry changes in scroll rows are thresholded and do not feed broad state
- [ ] Row rendering does not depend on `onAppear` as the only setup point
- [ ] Implicit animations use `.animation(_:value:)` for value-bound changes or `.animation(_:body:)` for narrower modifier scope
- [ ] No synchronous network/file I/O on the main thread
- [ ] Profiling done on Release build, real device
- [ ] `@State` is not used as an unspecified cache; every derived value has an explicit owner and refresh trigger
- [ ] `equatable()` is used only when comparison is cheaper than recomputation and inputs have stable value semantics
- [ ] Findings distinguish code-backed hypotheses from trace-backed evidence
- [ ] `@Observable` view models are `@MainActor`-isolated; types crossing concurrency boundaries are `Sendable`

## References

- Demystify SwiftUI performance (WWDC23): [references/demystify-swiftui-performance-wwdc23.md](references/demystify-swiftui-performance-wwdc23.md)
- Optimizing SwiftUI performance with Instruments: [references/optimizing-swiftui-performance-instruments.md](references/optimizing-swiftui-performance-instruments.md)
- Understanding hangs in your app: [references/understanding-hangs-in-your-app.md](references/understanding-hangs-in-your-app.md)
- Understanding and improving SwiftUI performance: [references/understanding-improving-swiftui-performance.md](references/understanding-improving-swiftui-performance.md)
- WWDC transcript sources: [references/wwdc-session-sources.md](references/wwdc-session-sources.md)
