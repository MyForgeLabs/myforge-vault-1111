---
name: stanfordnlp/dspy/docs/docs/tutorials/papillon/index.md
type: raw
source: external-repo
source_repo: stanfordnlp/dspy
source_path: docs/docs/tutorials/papillon/index.md
ingested_at: 2026-05-18T17:31:26
tags: ["#type/raw", "#source/external", "#source/github"]
---

Please refer to [this tutorial from the PAPILLON authors](https://colab.research.google.com/github/Columbia-NLP-Lab/PAPILLON/blob/main/papillon_tutorial.ipynb) using DSPy.

This tutorial demonstrates a few aspects of using DSPy in a more advanced context:

1. It builds a multi-stage `dspy.Module` that involves a small local LM using an external tool.
2. It builds a multi-stage _judge_ in DSPy, and uses it as a metric for evaluation.
3. It uses this judge for optimizing the `dspy.Module`, using a large model as a teacher for a small local LM.
