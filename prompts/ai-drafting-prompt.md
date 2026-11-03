# AI drafting prompt

## Overview

Copy this prompt into an AI assistant to create a first draft from approved source material.

## Before you begin

Collect the feature specification, verified UI labels, intended audience, supported versions, prerequisites, and known limitations. Do not provide confidential information to an unapproved AI service.

## Procedure

```text
You are assisting a technical writer. Draft a concise Markdown procedure for the
reader and goal below, using only the source facts provided.

Reader: [audience]
Goal: [task]
Source facts: [paste approved facts]
Required UI labels: [exact labels]
Prerequisites: [verified prerequisites]
Limitations: [known limitations]

Structure the draft with: # title, ## Overview, ## Before you begin,
## Procedure, and ## Troubleshooting. Use numbered steps for actions and
bullets for prerequisites. Use active voice, direct verbs, and the exact
terminology SafeRestore and recovery point. Include relative links only when
their target paths are supplied. Do not invent behavior, settings, outcomes,
dates, performance claims, or UI labels. Mark missing information as
[FACT CHECK: describe the question]. Return Markdown only.
```

## Troubleshooting

Treat the output as an unverified draft. Check every statement against authoritative product sources before publication.
