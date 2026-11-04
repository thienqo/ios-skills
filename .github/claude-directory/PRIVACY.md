# Privacy Policy

Effective date: November 4, 2026

This policy covers the thienqo-ios plugin, published by Thien Ngo from
<https://github.com/thienqo/ios-skills>.

## Summary

The plugin collects no personal data. It has no accounts, analytics, or servers
of its own, so the publisher does not receive your conversations, code, or files
through it.

## What the plugin contains

The plugin is a set of instructions and reference documents, plus four Python
scripts in two skills. It has no hooks, MCP servers, or background processes.

## Local scripts

The scripts run on your machine, and only when Claude uses them for a task in
the `ios-ettrace-performance` or `ios-memgraph-analysis` skill.

- They read the trace, dSYM, or memory graph files you point them at.
- They run local tools: `xcrun dwarfdump`, `xcrun simctl`, and `leaks`.
- They write results to the output location you choose or print them to the
  terminal.
- They make no network requests and do not read environment variables.

Memory graphs and traces can contain data from the app being analyzed, so review
what you capture.

## Data handled by Claude

Anything Claude reads while using a skill, including script output and files you
share, becomes part of your conversation with Claude. Anthropic's terms and
privacy policy cover that data, not this policy.

## Other services

- **Documentation links.** Skills link to Apple documentation through
  `sosumi.ai`, and to a few pages on `developer.apple.com` and other sites.
  When Claude opens a link, the site receives a normal web request for that
  page. Those sites have their own privacy policies.
- **Third-party tools.** Some skills describe installing or using tools such as
  Homebrew packages. Those tools contact their own services if you choose to
  install or run them.

## Usage statistics

Anthropic may show the publisher statistics about the plugin's listing, such as
installs, versions, runs, and error rates. Anthropic controls that data.

## Children

The plugin is a tool for software developers and is not intended for people
under 18.

## Changes and contact

Changes to this policy are published in the source repository, which keeps their
history. For questions, open an issue at
<https://github.com/thienqo/ios-skills/issues>.
