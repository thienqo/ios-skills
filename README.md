# Thienqo iOS Skills

95 Agent Skills for Swift, SwiftUI, and Apple-platform development, built
against Xcode 27, Swift 6.4, and the iOS 27 SDK, with a deployment floor of iOS
and iPadOS 26. Claude loads a skill when a task matches it, covering SwiftUI,
concurrency, data, testing, app frameworks, on-device AI, hardware, performance
diagnostics, and App Store delivery.

Skills are namespaced under the plugin, for example
`thienqo-ios-skills:swiftui-navigation`.

## What this plugin runs and fetches

This plugin contains instructions and reference documents. It has no hooks, MCP
servers, agents, or background processes, and it collects no data.

- **Local scripts.** Two skills include Python scripts that run only when Claude
  uses them for that task, on your machine. `ios-ettrace-performance` calls
  `xcrun dwarfdump` to match dSYM files. `ios-memgraph-analysis` calls
  `xcrun simctl` and `leaks` to capture and summarize memory graphs. These
  scripts read and write local files and make no network requests.
- **Documentation links.** Skills link to Apple documentation through
  `sosumi.ai`, which serves it as Markdown, and to a few `developer.apple.com`
  pages. Claude may open these links when it needs more detail.
- **Third-party tools.** Some skills describe installing or using tools such as
  Homebrew packages. Those tools contact their own services if you choose to
  install or run them.

See `PRIVACY.md` for the privacy policy.

## Source and license

Source and issues: <https://github.com/thienqo/ios-skills>

Licensed under the PolyForm Perimeter License 1.0.0; see `LICENSE`. Based on
work by dpearson2699. The adapted `swift-code-review` skill keeps its Apache-2.0
attribution. Apple frameworks, documentation, and trademarks belong to Apple
Inc. This project is independent and not endorsed by Apple.
