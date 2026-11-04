# Swift 6.4 (Xcode 27)

Swift 6.4 ships with Xcode 27 (announced September 15, 2026). Use it only when the project's toolchain is Xcode 27 or later; keep Swift 6.3 / Xcode 26 code paths otherwise. Async `defer`, cancellation shields, and `weak let` have deeper coverage in the `swift-concurrency` skill; Swift Testing changes are in `swift-testing`.

## Contents

- [Language](#language)
- [Standard library](#standard-library)
- [Performance and ownership](#performance-and-ownership)
- [Interop](#interop)
- [Tooling](#tooling)
- [Libraries](#libraries)
- [Sources](#sources)

## Language

| Feature | Notes |
|---|---|
| `anyAppleOS` | One availability entry instead of listing every Apple platform; also usable in `#if os` conditions |
| `@diagnose` | Changes how a warning group behaves inside one declaration: silence `deprecated declaration`, enable strict memory safety, promote warnings to errors |
| Async `defer` | `defer` bodies may call async functions |
| `~Sendable` | Explicitly opts a type out of `Sendable` without blocking `Sendable` subclasses (SE-0518) |
| `weak let` | Immutable weak reference; removes the need for `@unchecked Sendable` in some designs |
| `some`/`any` with optionals | No parentheses needed: `any P?` |
| Ignored task errors | Compiler warns when a task's thrown error is silently ignored |
| Memberwise init | Structs mixing internal and private properties get a second memberwise initializer usable from other files |
| Module selector `::` | `Rocket::SaturnV` disambiguates between modules. Apple advises against designing APIs that depend on it |

```swift
@available(anyAppleOS 27, *)
func useNewAPI() { }

@diagnose(DeprecatedDeclaration, as: ignored)
func legacyBridge() { /* calls deprecated API on purpose */ }
```

Verify exact `@diagnose` group names and syntax against the compiler before committing them.

## Standard library

- `withTaskCancellationShield`: inside it, cancellation checks return `false`, so cleanup can finish. Keep the region short.
- `mapKeyedValues`: like `mapValues`, but the closure also receives the key.
- A new file path type based on Swift System; `FilePath.stat()` and `FileDescriptor.stat()` (with `Stat`, `FileType`, `FileMode`, and related types) arrive in System.
- `Continuation`: compile-time check that it is resumed once, with `UnsafeContinuation` efficiency.

## Performance and ownership

- `Iterable`: `for` loops borrow elements in batches via spans, supporting noncopyable elements and avoiding reference counting. `for` prefers `Sequence` when both are available.
- `UniqueBox`, `UniqueArray`: standard library storage for noncopyable values without a fixed size limit.
- `Ref`, `MutableRef`: borrowed or mutable access to one value (for example, hoisting a dictionary lookup out of a loop).
- `borrow` and `mutate` accessors: in-place read-only or exclusive access without copying.
- `Equatable`, `Comparable`, `Hashable` work with noncopyable types; associated types may be noncopyable or non-escapable.
- `@inline(always)` (SE-0496) and `@specialized(where:)` (SE-0460) are covered in [swift-attributes-interop.md](swift-attributes-interop.md); pair `@inline(always)` with `final` on class methods.
- `withTemporaryAllocation` uses `OutputSpan`.

Reach for these only after measuring. Default to ordinary value types and arrays.

## Interop

- `@c` (SE-0495) exposes a Swift function to C and shipped in Swift 6.3; see [swift-attributes-interop.md](swift-attributes-interop.md). WWDC26 also shows `@implementation`, which implements a function already declared in a C header; verify its availability in the toolchain.
- `Span` bridges to C, and C++20 `std::span` bridges to Swift `Span`.
- Swift closures convert to `std::function`; `SWIFT_REFCOUNTED_PTR` bridges smart pointers to Swift classes.
- Official Swift SDK for Android; Embedded Swift gains existentials and untyped throws.

## Tooling

- Swift Build (the open-source Xcode build system) is the default backend for SwiftPM.
- Xcode 27 removes the ld64 linker; `-ld_classic` is no longer supported.
- `swift test` supports `--maximum-repetitions` with `--repeat-until`.
- A computed property with both an `init` accessor and a literal initial value fails to compile when the getter comes first; declare the `init` accessor first.

## Libraries

- Subprocess 1.0: cross-platform process launching, streaming output through `AsyncBufferSequence`, `strings()` for line-by-line reads.
- Foundation: `ProgressManager` for async progress reporting with typed metadata; faster `Data` operations and URL parsing.

## Sources

- https://sosumi.ai/videos/play/wwdc2026/262
- https://developer.apple.com/wwdc26/guides/swift/
- https://sosumi.ai/documentation/xcode-release-notes/xcode-27-release-notes
