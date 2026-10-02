# Execution record

Local execution of `python3 pipeline.py examples/energy.csv output/energy.json`. The input and output shown come from the repository example or test fixtures.

- `python3 pipeline.py examples/energy.csv output/energy.json` — exit 0.
- `python3 -m unittest discover -s tests -v` — exit 0.

The image renders the captured terminal output. [Full transcript](screenshots/execution.txt).

Latest local test output:

```text
test_bad_date_rejected (test_pipeline.PipelineTests.test_bad_date_rejected) ... ok
test_decimal_total (test_pipeline.PipelineTests.test_decimal_total) ... ok
test_duplicates_rejected (test_pipeline.PipelineTests.test_duplicates_rejected) ... ok
test_failed_validation_preserves_output (test_pipeline.PipelineTests.test_failed_validation_preserves_output) ... ok
test_nonfinite_rejected (test_pipeline.PipelineTests.test_nonfinite_rejected) ... ok
test_valid_dataset_published (test_pipeline.PipelineTests.test_valid_dataset_published) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.002s

OK
```

This record covers the local commands and fixtures shown. External services and deployment remain unverified unless explicitly listed.
