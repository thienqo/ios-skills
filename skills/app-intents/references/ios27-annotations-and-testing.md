# App Intents in iOS 27: Annotations, New Protocols, Testing

Covers the iOS 27 additions: on-screen entity annotations for Siri, new intent and entity protocols, and the AppIntentsTesting framework. API names come from Apple's App Intents updates page, the iOS 27 release notes, and WWDC26 sessions 343 and 295. Exact signatures are not reproduced here; confirm them in the 27 SDK.

## Contents

- [On-screen awareness annotations](#on-screen-awareness-annotations)
- [Intent behavior protocols](#intent-behavior-protocols)
- [Entity protocols and types](#entity-protocols-and-types)
- [App schemas](#app-schemas)
- [Other annotation points](#other-annotation-points)
- [AppIntentsTesting](#appintentstesting)
- [Common mistakes](#common-mistakes)
- [Sources](#sources)

## On-screen awareness annotations

Tell the system which entity is on screen so people can act on it by asking Siri.

| Situation | Annotation |
|---|---|
| One primary entity fills the screen | `.userActivity` on the view, with the entity attached to the `NSUserActivity` |
| One of many entities on screen | `.appEntityIdentifier` on each entity's view |
| A `List` with selection | `.appEntityIdentifier(forSelectionType:)` on the list; the system fetches identifiers lazily and finds selected entities scrolled off screen |
| Custom canvas or non-standard subview | Custom view annotation |
| UIKit / AppKit | `AppEntityAnnotatable`, `UICollectionViewAppIntentsDataSource`, `appEntityUIElementProvider` |

Per-row annotations disappear when the row leaves the view hierarchy; use the collection annotation for long lists. Implement `displayRepresentations` on an entity query so Siri can read lightweight text without fetching full content. Annotate the real entity ID, not a related identifier (a test in session 295 caught a view passing a calendar identifier instead of the event ID).

## Intent behavior protocols

| API | Purpose |
|---|---|
| `supportedModes` (`IntentModes`) | Foreground, background, or both; read `currentMode` in `perform()` |
| `allowedExecutionTargets` (`IntentExecutionTargets`) | Whether the app, an App Intents extension, or a widget extension may run an intent or entity query |
| `LongRunningIntent` | Extends background runtime through `performBackgroundTask`, with progress |
| `CancellableIntent`, `IntentCancellationReason` | Cleanup on cancellation; distinguishes cancel from timeout |
| `UndoableIntent` | Reverses the intent's effect |
| `RunSystemShortcutIntent` | Lets interactive widgets run shortcuts, system actions, or open another app |
| `ProvidesDialog` | Return a custom `IntentDialog` |
| `ShowsSnippetView` | Return a SwiftUI view as the response |
| `AppIntentError(description:)` | Localized failure text, or wrap an error that conforms to `CustomLocalizedStringResourceConvertible` |

## Entity protocols and types

| API | Purpose |
|---|---|
| `SyncableEntity` | Stable entity identifiers across devices so a task can continue on another device |
| `OwnershipProvidingEntity` | Ownership state so Siri confirms destructive actions on shared or public entities. Conform only entities people can share; keep the state current. Siri treats entities as private by default |
| `RelevantEntities` | Lets Apple Intelligence suggest media entities (songs, albums) during workouts |
| `IntentValueRepresentation` | In `transferRepresentation`, bridges entities to system intent value types |
| `EntityCollection` | Stores identifiers only; resolves `AppEntity` instances on demand |
| `AppUnionValue`, `AppUnionValueCasesProviding` | Union-type Shortcuts parameters with picker UI |
| `IndexedEntityQuery` | System retrieves indexed entities by identifier from Spotlight; supports reindexing |
| `IntentValueQuery` | Structured search when entities are not all indexed ahead of time |
| `IntentDonationManager` | Donate UI interactions |

## App schemas

- `.system.searchInApp` (renamed from the iOS 17 `.system` search schema): lets people search in your app with Siri without indexed entities.
- New domains include Maps (`NavigationSession` start/stop) and Clock (stopwatch start, stop, pause, lap). AudioSearch pairs with `IntentValueQuery`.
- Notes schemas `notes.createNote` and `notes.updateNote` accept a name of type `AttributedString`. `calendar.deleteEvents` is renamed `calendar.deleteEvent`.

## Other annotation points

`CSSearchableIndex.indexAppEntities` populates the Spotlight semantic index. `UNMutableNotificationContent.appEntityIdentifiers` annotates notifications. Now Playing `appEntityIdentifiers` are ordered most to least specific. `AlarmConfiguration.appEntityIdentifier` annotates alarms and timers.

## AppIntentsTesting

Out-of-process testing of intents, entities, queries, Spotlight indexing, and view annotations without UI scripting.

Setup:

1. Add a UI Testing bundle (XCUITest). Same development team as the app. Choose the app as target.
2. `import AppIntentsTesting` in an `XCTestCase`. The test target does not import app code; it needs only the app's bundle identifier.
3. The app runs in a separate process; no state is shared.

Core API (names from session 295):

- `IntentDefinitions(...)` with the app bundle identifier exposes every intent, entity, and query.
- `intents[...]` returns an `IntentDefinition`; `makeIntent` builds an instance; `run()` executes in the app; read results through `value` (dynamic member lookup, e.g. `result.value.title`).
- `AppEnum` parameters take the raw string value. Custom types need `IntentValueConvertibleWrapper`.
- `entities(matching:)` on an entity definition runs its string query on device. Passing a string for an entity parameter calls the string query and uses the first match.
- `spotlightQuery()` returns Spotlight-indexed representations matching a string.
- `viewAnnotations()` on an entity definition returns the annotations the system sees on screen; assert the count and read `entity`.
- Chain intents by passing one `run()` result into the next, like Shortcuts.
- Parameter names and types do not auto-complete because the test does not build against the app.

Test-only intents seed and reset data and navigate directly to screens. Declare them inside `#if DEBUG` and mark them non-discoverable (session 295 uses `isDiscoverable: false`), so only tests can reach them. A test-only intent may wrap any app functionality, including features that do not use App Intents yet. Confirm the exact declaration in the 27 SDK.

Test layers: unit-test actions, data, and queries first; integration-test Spotlight, view annotations, and cross-app behavior; still test manually in Siri and Shortcuts.

## Common mistakes

- Annotating rows individually in a long list instead of the collection annotation.
- Conforming private entities to `OwnershipProvidingEntity`, or letting ownership state go stale.
- Shipping test-only intents without `#if DEBUG` and non-discoverable settings.
- Assuming `LongRunningIntent` removes the need for cancellation handling.
- Forgetting to gate iOS 27 protocols with `#available(iOS 27, *)`.

## Sources

- https://sosumi.ai/documentation/updates/appintents
- https://sosumi.ai/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes
- https://sosumi.ai/videos/play/wwdc2026/343
- https://sosumi.ai/videos/play/wwdc2026/295
