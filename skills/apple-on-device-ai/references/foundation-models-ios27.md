# Foundation Models in iOS 27

iOS 27 / macOS 27 / visionOS 27 / watchOS 27 additions to Foundation Models. Everything here needs the 27.0 SDK (Xcode 27) and an availability check when the deployment target is iOS 26. The iOS 26 surface in [foundation-models.md](foundation-models.md) still applies.

## Contents

- [What changed](#what-changed)
- [LanguageModel protocol](#languagemodel-protocol)
- [Private Cloud Compute model](#private-cloud-compute-model)
- [Multimodal prompts](#multimodal-prompts)
- [Dynamic Profiles](#dynamic-profiles)
- [Core AI model in a session](#core-ai-model-in-a-session)
- [Tooling](#tooling)
- [Common mistakes](#common-mistakes)
- [Sources](#sources)

## What changed

| Area | iOS 26 | iOS 27 |
|---|---|---|
| Model | `SystemLanguageModel` only | Any `LanguageModel`: system, Private Cloud Compute, Core AI, custom/server |
| Input | Text | Text plus images through `Attachment` |
| Session config | Fixed at init | `LanguageModelSession.DynamicProfile` switches model, tools, instructions, temperature, reasoning level |
| Transcript | Prompts, responses, tool calls | Adds reasoning entries (`Transcript.Entry.reasoning(_:)`) |
| Measurement | Manual | Foundation Models instrument in Instruments, Evaluations framework |

## LanguageModel protocol

`LanguageModel` (iOS 27.0+) is the seam between a model and `LanguageModelSession`. Same session API, different model:

```swift
let session = LanguageModelSession(model: MyCustomServerLanguageModel())
let response = try await session.respond(to: "Tell me a joke!")
```

Requirements: `capabilities`, `executorConfiguration`, an `Executor`, `supportsDataAttachmentType(_:)`, `supportsDataEntryType(_:)`. The executor does the work: it receives a `LanguageModelExecutorGenerationRequest` (transcript, tools, schema, options) and streams events back through a `LanguageModelExecutorGenerationChannel`. Keep the conforming type lightweight.

Built-in conformers: `SystemLanguageModel`, `PrivateCloudComputeLanguageModel`. Check `model.capabilities` (`LanguageModelCapabilities`: guided generation, reasoning, tool calling, vision) before using a feature. Ship custom providers as Swift packages.

## Private Cloud Compute model

Larger server-side model with the same session API.

```swift
let model = PrivateCloudComputeLanguageModel()

guard model.isAvailable else {
    // inspect model.availability (PrivateCloudComputeLanguageModel.Availability)
    return
}

let session = LanguageModelSession(model: model)
let response = try await session.respond(to: "Summarize this note.")
```

- Needs the managed entitlement `com.apple.developer.private-cloud-compute`. Request it through Apple's Private Cloud Compute developer page; eligibility requirements apply.
- Check `availability` (device not eligible, system not ready) before use.
- Read `quotaUsage` (`PrivateCloudComputeLanguageModel.QuotaUsage`: limits, status, reset date) and surface quota state in UI.
- Handle `PrivateCloudComputeLanguageModel.Error`: quota reached, network failure, service unavailable. Keep an on-device or non-AI fallback.
- Also exposes `contextSize`, `supportedLanguages`, `supportsLocale(_:)`.

## Multimodal prompts

Wrap images in `Attachment` inside the prompt. Accepted sources: `CGImage`, `CIImage`, `CVPixelBuffer` (camera, video frames), image `URL` (type inferred from the URL, so it must point at a real image file).

- Pass `orientation` for images with no rotation applied, such as AVFoundation frames.
- The framework scales and converts color for you.
- `.label(_:)` on an attachment lets tools refer to that image.
- Pair images with a `@Generable` enum and greedy sampling to get one of your predefined labels.
- Vision-backed tools ship with the framework: `OCRTool` (text extraction) and `BarcodeReaderTool`.
- Custom tools take an `ImageReference` argument; resolve it against the session transcript inside `call(arguments:)`.
- Check `capabilities` for vision support on the chosen model first.

## Dynamic Profiles

`LanguageModelSession.DynamicProfile` lets one session change configuration as app state changes. `body` must resolve to a single `Profile`; a `Profile` binds instructions and tools to model settings.

Modifiers:

- Model and sampling: `model(_:)`, `temperature(_:)`, `samplingMode(_:)`, `reasoningLevel(_:)`, `maximumResponseTokens(_:)`, `toolCallingMode(_:)`
- History: `historyTransform(_:)` changes what the model sees without changing the stored transcript
- Lifecycle: `onActivate`, `onDeactivate`, `onPrompt`, `onReasoning`, `onResponse`, `onToolCall`, `onToolOutput`
- Errors: `transcriptErrorHandlingPolicy(_:)`

```swift
Profile {
    // instructions and tools for the task
}
.historyTransform { history in
    Array(history.suffix(20))
}
```

Use a profile to move from a cheap on-device model to a server model for hard tasks, or to expose editing tools only while the user is editing. Prefer one session with profiles over rebuilding sessions and losing the transcript.

## Core AI model in a session

`CoreAILanguageModel` (from the `coreai-models` package, `CoreAILM` product) runs an exported open-weights model through the same session API. Requires iOS 27 / macOS 27 and Xcode 27.

```swift
import FoundationModels
import CoreAILanguageModels

guard let modelURL = Bundle.main.url(forResource: "YourModelFolder", withExtension: nil) else { return }

let model = try await CoreAILanguageModel(resourcesAt: modelURL)
let session = LanguageModelSession(model: model)
let response = try await session.respond(to: "Summarize the key points: ...")
```

Steps: export with `uv run coreai.llm.export HF_ID` (add `--platform iOS` for iOS), bundle the output folder (`.aimodel` plus tokenizer), add the `coreai-models` package. Loading is async; start before the user needs it. Reasoning models add `Transcript.Entry.reasoning(_:)`, which stays out of the user-facing response. For raw model execution without a session, see [core-ai.md](core-ai.md).

## Tooling

- **Foundation Models instrument** (Xcode 27 Instruments): load times, token counts, latency.
- **Evaluations framework**: verifies AI feature behavior under dynamic conditions beyond unit tests.
- Key-value cache tuning: Apple's "Optimizing key-value caching in language model sessions" article.

## Common mistakes

- Using iOS 27 types without `#available(iOS 27, *)` on an iOS 26 deployment target.
- Calling `PrivateCloudComputeLanguageModel` without the managed entitlement or without handling quota and network errors.
- Sending images to a model whose `capabilities` lack vision.
- Rebuilding sessions to change model or tools instead of using a Dynamic Profile.
- Showing reasoning entries to users.

## Sources

- https://sosumi.ai/documentation/foundationmodels
- https://sosumi.ai/documentation/foundationmodels/languagemodel
- https://sosumi.ai/documentation/foundationmodels/privatecloudcomputelanguagemodel
- https://sosumi.ai/documentation/foundationmodels/languagemodelsession/dynamicprofile
- https://sosumi.ai/documentation/foundationmodels/analyzing-images-with-multimodal-prompting
- https://sosumi.ai/documentation/foundationmodels/running-a-core-ai-model-in-a-foundation-models-session
