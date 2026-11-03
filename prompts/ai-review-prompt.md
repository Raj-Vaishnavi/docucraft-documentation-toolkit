# AI review prompt

## Overview

Use this prompt to request a structured editorial review of a draft. It does not certify technical accuracy.

## Before you begin

Provide only content approved for the AI service you use. Include the intended audience, task, and authoritative reference material where permitted.

## Procedure

```text
Review the Markdown draft below for reader clarity and writing quality.
Audience and task: [audience and goal]
Approved reference facts: [source material or links]
Draft: [paste draft]

Report findings under these headings:
1. Structure and missing information
2. Ambiguous or hard-to-follow steps
3. Terminology and UI-label inconsistencies
4. Grammar and concise wording
5. Claims that need human fact-checking

For each finding, quote only the short relevant phrase, explain the issue,
and suggest a minimal revision. Compare product claims with the supplied
reference facts; if evidence is absent, label the claim NEEDS HUMAN CHECK.
Do not invent facts or silently rewrite the full document. Do not state that
the draft is technically correct unless each claim is supported by a cited
reference. Return the review only.
```

## Troubleshooting

An AI review can miss errors or introduce suggestions unsupported by evidence. A writer and product expert must decide what to accept.
