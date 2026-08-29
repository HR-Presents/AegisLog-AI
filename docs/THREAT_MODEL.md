# Threat model

## Assets

Production logs, credentials accidentally embedded in logs, investigation reports, local configuration, and any future AI-provider credentials.

## Primary risks

- sensitive data disclosure through reports or future external AI calls
- malicious or misleading log text influencing AI explanations
- false positives causing unsafe administrator actions
- very large or malformed logs exhausting local resources
- terminal escape/control characters embedded in untrusted logs

## Current mitigations

- local-first processing
- common-secret redaction
- bounded output and AI-context sizes
- evidence-oriented wording and explicit uncertainty
- no automatic remediation actions
- API secrets excluded from normal configuration

## Planned mitigations

Normalize terminal control characters, streaming size limits, configurable allow/deny patterns, stronger structured redaction, provider isolation, explicit consent before remote processing, and fuzz/property tests for parsers.
