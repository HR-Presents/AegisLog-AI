# AI investigation safety

Generative analysis must never be the sole source of a security verdict. AegisLog's AI layer receives deterministic findings plus selected redacted context and should clearly distinguish observed evidence, likely explanations, uncertainty, and recommended next checks.

Log content is untrusted data and may contain prompt-injection-like text. Future provider prompts must instruct models to treat log text only as evidence, not as commands. Model output must not automatically execute shell commands or remediation actions.
