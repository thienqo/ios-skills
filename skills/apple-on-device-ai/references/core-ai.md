# Core AI (iOS 27+)

Core AI is a memory-safe Swift framework for loading, specializing, and running your own models fully on device. Requires iOS 27 / macOS 27 and Xcode 27. Core ML stays supported for existing models; evaluate Core AI for new LLM-style or custom-compute workloads.

## Contents

- [Types](#types)
- [Load and run](#load-and-run)
- [Neural Engine behavior in iOS 27](#neural-engine-behavior-in-ios-27)
- [Debugging](#debugging)
- [Common mistakes](#common-mistakes)
- [Sources](#sources)

## Types

| Type | Role |
|---|---|
| `AIModel` | Loads and specializes a model; entry to its inference functions |
| `AIModelAsset` | Inspects and modifies a model file: metadata, summary, derived artifacts |
| `InferenceFunction` | Runs one model function, sync or async, with inputs, states, outputs |
| `NDArray` | Multidimensional array for inputs and outputs, typed and raw views |
| `ComputeStream` | Orders asynchronous inference work |
| `SpecializationOptions`, `ComputeUnitKind` | Pick CPU, GPU, or Neural Engine |
| `AIModelCache` | Stores specialized models; sets purge policy |

## Load and run

1. Create an `AIModel` from a file URL with `init(contentsOf:options:)`, or call `specialize(contentsOf:options:cache:cachePolicy:)` to reuse a cached specialization.
2. Get a function with `loadFunction(named:)`; list names with `functionNames`.
3. Inspect inputs and outputs with `functionDescriptor(for:)` or `InferenceFunction.descriptor`.
4. Call `run(inputs:states:outputViews:)` with `NDArray` inputs. The call is async.

Specialize ahead of first use and cache the result; specialization is the slow step. To drive an LLM through the Foundation Models session API instead, see [foundation-models-ios27.md](foundation-models-ios27.md#core-ai-model-in-a-session).

## Neural Engine behavior in iOS 27

From the iOS 27 release notes:

- Background Neural Engine access is restricted, like GPU limits. Background inference needs the entitlement `com.apple.developer.background-tasks.continued-processing.inference`.
- Loading models over 1 GB is faster.
- Neural Engine memory counts against your app process and shows in the Allocations instrument.

## Debugging

Core AI Debugger, Instruments, and a debug gauge are available in Xcode 27. Use the Foundation Models instrument when the model runs inside a `LanguageModelSession`.

## Common mistakes

- Starting Neural Engine work from a background task without the inference entitlement.
- Specializing on every launch instead of using `AIModelCache`.
- Budgeting memory as if Neural Engine allocations were free; they are attributed to the app.
- Rewriting working Core ML pipelines without a measured reason.

## Sources

- https://sosumi.ai/documentation/coreai
- https://sosumi.ai/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes
