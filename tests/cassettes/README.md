# VCR Test Cassettes

This directory contains **VCR cassettes** - recorded HTTP interactions from provider API tests.

## What are VCR Cassettes?

VCR (Video Cassette Recorder) is a testing technique that:
1. **Records** HTTP requests and responses on the first test run
2. **Replays** the recorded interactions on subsequent runs
3. **Eliminates** the need for API keys after initial recording

## Purpose

- ✅ **Run integration tests without API keys** (after recording)
- ✅ **Deterministic tests** - same responses every time
- ✅ **Fast tests** - no network calls
- ✅ **Cost-effective** - no repeated API charges
- ✅ **Offline testing** - work without internet

## File Format

Cassettes are stored as YAML files with sanitized data:

```yaml
interactions:
- request:
    method: POST
    uri: https://api.openai.com/v1/chat/completions
    headers:
      authorization: REDACTED  # API keys filtered out
  response:
    status:
      code: 200
    body:
      string: '{"choices":[{"message":{"content":"Test response"}}]}'
```

## Security

**Safe to commit to git:**
- ✅ API keys are automatically filtered/redacted
- ✅ Sensitive headers removed
- ✅ Only request/response structure retained

See `tests/models/test_providers_vcr.py` for filter configuration.

## Usage

### Recording New Cassettes

```bash
# 1. Set your API key
export OPENAI_API_KEY=sk-your-real-key

# 2. Delete old cassette (if updating)
rm tests/cassettes/test_openai_vcr_basic.yaml

# 3. Run the test (records new cassette)
pytest tests/models/test_providers_vcr.py::test_openai_vcr_basic -v

# 4. Cassette is created
ls tests/cassettes/test_openai_vcr_basic.yaml
```

### Running Tests with Cassettes

```bash
# No API key needed - replays from cassette
pytest tests/models/test_providers_vcr.py -v
```

### Updating Cassettes

When APIs change or you need fresh recordings:

```bash
# Delete all cassettes
rm tests/cassettes/*.yaml

# Re-record (requires API keys)
export OPENAI_API_KEY=sk-your-key
export ANTHROPIC_API_KEY=sk-ant-your-key
pytest tests/models/test_providers_vcr.py -v

# Commit updated cassettes
git add tests/cassettes/*.yaml
git commit -m "Update VCR cassettes"
```

## File Naming Convention

Cassette files are named after their test functions:

| Test Function | Cassette File |
|---------------|---------------|
| `test_openai_vcr_basic` | `test_openai_vcr_basic.yaml` |
| `test_anthropic_vcr_basic` | `test_anthropic_vcr_basic.yaml` |
| `test_google_vcr_basic` | `test_google_vcr_basic.yaml` |

## When to Use VCR vs Mocks

| Approach | Best For |
|----------|----------|
| **Mocks** | Unit tests, testing logic, fast iteration |
| **VCR** | Integration tests, realistic responses, API structure validation |
| **Real API** | Final validation, current API compatibility checks |

## Troubleshooting

### Cassette not being used
```bash
# Check cassette exists
ls tests/cassettes/

# Check VCR is installed
pip list | grep vcr

# Check test has @pytest.mark.vcr decorator
grep -n "mark.vcr" tests/models/test_providers_vcr.py
```

### Need to force re-record
```bash
# Delete cassette
rm tests/cassettes/test_name.yaml

# Run test with API key
export API_KEY=sk-your-key
pytest tests/models/test_providers_vcr.py::test_name -v
```

### API keys visible in cassette
Check `vcr_config` fixture in `test_providers_vcr.py`:
```python
"filter_headers": [
    ("authorization", "REDACTED"),
    ("x-api-key", "REDACTED"),
    # Add more headers as needed
],
```

## Learn More

- VCR.py Documentation: https://vcrpy.readthedocs.io/
- pytest-vcr: https://pytest-vcr.readthedocs.io/
- Testing Guide: See `tests/TESTING_WITH_API_KEYS.md`

## Current Cassettes

This directory may be empty initially. Cassettes are created when VCR tests run for the first time with real API keys.

To see available cassettes:
```bash
ls -lh tests/cassettes/
```

