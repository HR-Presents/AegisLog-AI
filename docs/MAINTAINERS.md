# Maintainer notes

Before accepting a new detection, ask whether it is explainable, testable, and likely to create unacceptable false positives. Before accepting a new collector/provider, identify its permissions, trust boundary, sensitive-data path, failure mode, and resource limits.

Keep sample data synthetic. Keep remote AI optional. Keep automatic remediation out of the default execution path.
