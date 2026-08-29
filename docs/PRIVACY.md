# Privacy model

AegisLog is local-first. V0.2 parsing, rules, anomaly scoring, correlation, reports, and `ask` operate locally.

Future external AI support must be opt-in. Before external processing, AegisLog should minimize context and redact recognized passwords, tokens, API keys, and secrets. Users remain responsible for checking whether logs contain personal, confidential, regulated, or otherwise sensitive data that the built-in redactor does not recognize.

Configuration files store provider/model preferences only. Secret API credentials should be supplied through environment variables or secure operating-system facilities rather than written into AegisLog configuration.
