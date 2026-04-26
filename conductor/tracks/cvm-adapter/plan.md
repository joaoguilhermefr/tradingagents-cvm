# Track Implementation Plan: Stabilize and Document CVM Market Adapter

**Track ID:** `cvm-adapter`  
**Last Updated:** 2026-04-10  
**Status:** New

---

## Phase 1: Code Analysis & Planning

### Task 1.1: Analyze Existing CVM Adapter Code
- [ ] Review existing CVM market adapter implementation
- [ ] Identify deviations from Python Code Style Guide
- [ ] Map current market-specific configurations
- [ ] List missing type hints and docstrings
- [ ] Document current test coverage
- [ ] Identify code duplication opportunities
- [ ] Create refactoring checklist

**Acceptance Criteria:**
- Document prepared with findings
- Refactoring checklist created
- No code changes yet

---

### Task 1.2: Define CVM Market Configuration Schema
- [ ] Review current configuration handling
- [ ] Design market configuration structure (as Pydantic model)
- [ ] Define required vs. optional parameters
- [ ] Create configuration validation logic
- [ ] Document all configuration options

**Acceptance Criteria:**
- Configuration schema documented
- Validation logic designed
- Example configurations prepared

---

## Phase 2: Code Refactoring & Type Safety

### Task 2.1: Refactor CVM Market Adapter Module
- [ ] Update module organization (separation of concerns)
- [ ] Add type hints to all functions (Python 3.10+ unions)
- [ ] Add Google-style docstrings to all public functions
- [ ] Remove hardcoded market parameters
- [ ] Consolidate duplicate code
- [ ] Add debug logging for troubleshooting

**Dependencies:** Phase 1 complete

**Acceptance Criteria:**
- All functions have type hints
- All public functions have docstrings
- Code follows Style Guide
- No hardcoded values remain

**Tests Required:**
- [ ] Unit test: Configuration parsing
- [ ] Unit test: Market hours validation
- [ ] Unit test: Data source fallbacks

---

### Task 2.2: Implement Market Configuration Management
- [ ] Create `CvmMarketConfig` Pydantic model
- [ ] Implement configuration validation
- [ ] Add configuration merging (defaults + overrides)
- [ ] Implement configuration serialization/deserialization
- [ ] Add configuration logging at startup

**Dependencies:** Task 2.1

**Acceptance Criteria:**
- Configuration can be created from dict
- Validation enforces required fields
- Invalid configurations raise informative errors
- Configuration properly documented

**Tests Required:**
- [ ] Unit test: Create valid config
- [ ] Unit test: Invalid config raises error
- [ ] Unit test: Configuration merging
- [ ] Unit test: Configuration serialization

---

### Task 2.3: Implement Trading Calendar for Brazilian Market
- [ ] Create `BrazilianTradingCalendar` class
- [ ] Load Brazilian holiday calendar
- [ ] Implement trading hours check
- [ ] Implement next/previous trading day calculations
- [ ] Handle edge cases (pre/post-market hours)

**Dependencies:** Task 2.1

**Acceptance Criteria:**
- Calendar correctly identifies trading days
- Respects Brazilian holidays
- Handles timezone conversions
- Clear error messages for invalid dates

**Tests Required:**
- [ ] Unit test: Is trading day (holiday)
- [ ] Unit test: Is trading day (weekend)
- [ ] Unit test: Is trading day (valid day)
- [ ] Unit test: Next trading day calculation
- [ ] Unit test: Trading hours validation
- [ ] Unit test: Timezone conversion

---

## Phase 3: Market Data Integration

### Task 3.1: Implement CVM Market Data Fetcher
- [ ] Create `CvmMarketDataFetcher` class
- [ ] Implement data fetching from yfinance (B3 format: .SA suffix)
- [ ] Implement error handling for missing data
- [ ] Implement retry logic with exponential backoff
- [ ] Add data validation (NaN, zero prices, etc.)
- [ ] Log data fetch operations

**Dependencies:** Task 2.2

**Acceptance Criteria:**
- Successfully fetch Brazilian stock data
- Handle API failures gracefully
- Retry on transient errors
- Validate fetched data
- Clear error messages for data issues

**Tests Required:**
- [ ] Unit test: Fetch valid stock data
- [ ] Unit test: Handle missing ticker
- [ ] Unit test: Handle API timeout
- [ ] Unit test: Data validation (NaN handling)
- [ ] Unit test: Retry logic
- [ ] Integration test: Real data fetch (mock network)

---

### Task 3.2: Integrate Market Data with Agent Framework
- [ ] Update agent data access to use CVM market fetcher
- [ ] Ensure agents respect trading calendar
- [ ] Implement market-specific data formatting
- [ ] Add market-aware logging in agents
- [ ] Verify no regressions in existing agents

**Dependencies:** Task 3.1, Task 2.2

**Acceptance Criteria:**
- Agents use CVM market data correctly
- Trading calendar respected in analysis
- No agent functionality broken
- All existing tests still pass

**Tests Required:**
- [ ] Integration test: Analyst with CVM data
- [ ] Integration test: Trader with market hours
- [ ] Unit test: Market-specific formatting

---

## Phase 4: Comprehensive Testing

### Task 4.1: Create Unit Tests for CVM Adapter
- [ ] Write tests for `CvmMarketConfig` (validation, merging)
- [ ] Write tests for `BrazilianTradingCalendar` (all methods)
- [ ] Write tests for `CvmMarketDataFetcher` (success + failures)
- [ ] Write tests for market-specific functions
- [ ] Achieve >80% code coverage for adapter

**Dependencies:** Phase 3

**Acceptance Criteria:**
- >80% code coverage
- All edge cases tested
- All tests passing
- Mock data properly setup

**Command:**
```bash
pytest tests/cvm_adapter/ --cov=tradingagents.market.cvm --cov-report=term-missing
```

---

### Task 4.2: Create Integration Tests
- [ ] Write tests for full workflow with CVM market
- [ ] Test with sample Brazilian stock data
- [ ] Test with multiple LLM providers (mock)
- [ ] Test configuration variations
- [ ] Test error recovery scenarios

**Dependencies:** Task 4.1

**Acceptance Criteria:**
- Integration tests cover major workflows
- Tests pass with all LLM configs
- Tests handle failures gracefully
- >80% overall coverage maintained

**Tests Required:**
- [ ] Integration test: Full trading cycle (CVM market)
- [ ] Integration test: Multiple stocks analysis
- [ ] Integration test: Market hours respect
- [ ] Integration test: LLM fallback handling

---

### Task 4.3: Verify No Regressions
- [ ] Run full test suite: `pytest tests/`
- [ ] Check overall code coverage remains >80%
- [ ] Test with existing configurations
- [ ] Verify existing functionality unchanged
- [ ] Document any breaking changes

**Dependencies:** Task 4.2

**Acceptance Criteria:**
- All existing tests pass
- No code coverage regression
- Breaking changes documented
- Compatibility notes added to docs

---

## Phase 5: Configuration & Documentation

### Task 5.1: Consolidate Configuration
- [ ] Merge CVM config into `DEFAULT_CONFIG`
- [ ] Create market-specific config examples
- [ ] Update configuration schema documentation
- [ ] Add configuration validation to framework startup
- [ ] Create configuration migration guide (if needed)

**Dependencies:** Task 2.2

**Acceptance Criteria:**
- `DEFAULT_CONFIG` includes CVM market config
- Example configs for common scenarios
- Configuration validation in place
- Docs describe all options

**Configuration Examples:**
```python
# Brazilian market (default)
DEFAULT_CONFIG = {
    "market": "brazilian",
    "exchange": "B3",
    "trading_hours": {"open": "10:00", "close": "17:50"},
    ...
}

# US market alternative
US_CONFIG = {
    "market": "us",
    "exchange": "NASDAQ",
    "trading_hours": {"open": "09:30", "close": "16:00"},
    ...
}
```

---

### Task 5.2: Create CVM Market User Guide
- [ ] Create `docs/cvm-market-guide.md` with:
  - Overview of Brazilian market integration
  - Supported assets and data sources
  - Configuration step-by-step guide
  - Example usage (Python + CLI)
  - Troubleshooting common issues
  - Performance expectations
  - Known limitations
- [ ] Include configuration examples
- [ ] Add FAQ section
- [ ] Document API keys/authentication needed

**Dependencies:** Task 5.1

**Acceptance Criteria:**
- Guide is complete and clear
- Examples are runnable
- All configuration options explained
- Troubleshooting covers common issues

---

### Task 5.3: Update README with CVM Example
- [ ] Add CVM market example to main README
- [ ] Show configuration for Brazilian market
- [ ] Show Python API usage example
- [ ] Show CLI usage for Brazilian stocks
- [ ] Link to full CVM guide
- [ ] Mention required API keys (yfinance, etc.)

**Dependencies:** Task 5.2

**Acceptance Criteria:**
- README updated with clear example
- Example is runnable and correct
- Link to full guide provided
- API requirements mentioned

---

### Task 5.4: Add Docstrings & Comments
- [ ] Review all CVM adapter code for docstrings
- [ ] Add module-level docstrings
- [ ] Add complex logic comments (explain why, not what)
- [ ] Add usage examples to docstrings
- [ ] Cross-reference related modules

**Dependencies:** Phase 3

**Acceptance Criteria:**
- All public APIs documented
- Complex logic explained
- Examples in docstrings where helpful

---

## Phase 6: Integration & Verification

### Task 6.1: Multi-LLM Integration Testing
- [ ] Test with OpenAI GPT models
- [ ] Test with Google Gemini models
- [ ] Test with Anthropic Claude models
- [ ] Test with local Ollama (Qwen 3.5 35B)
- [ ] Document any model-specific behavior
- [ ] Verify fallback chains work

**Dependencies:** Phase 4

**Acceptance Criteria:**
- Works with all supported LLM providers
- Model-specific behaviors documented
- Fallback chains tested
- Performance acceptable for each provider

---

### Task 6.2: Data Source Validation
- [ ] Verify yfinance fetches Brazilian stocks correctly
- [ ] Validate data quality (no NaN, valid prices)
- [ ] Test with real market data (sample)
- [ ] Verify trading calendar alignment with B3
- [ ] Document data source limitations

**Dependencies:** Task 3.1

**Acceptance Criteria:**
- Data fetched successfully
- Data quality verified
- Calendar matches actual B3 schedule
- Limitations documented

---

### Task 6.3: Conductor - User Manual Verification (Phase 6)
- [ ] Execute full workflow with CVM config
- [ ] Verify all deliverables present
- [ ] Test documentation with fresh user perspective
- [ ] Verify examples run correctly
- [ ] Check for any missing pieces
- [ ] Create final verification checklist

**Dependencies:** All previous phases

**Acceptance Criteria:**
- All features working as specified
- Documentation complete and accurate
- Examples tested and working
- No known issues remaining

---

## Summary

| Phase | Tasks | Est. Duration | Key Deliverables |
|-------|-------|---------------|------------------|
| 1 | 2 | 1-2 days | Analysis, planning docs |
| 2 | 3 | 1-2 days | Refactored code, config schema |
| 3 | 2 | 1-2 days | Market data integration |
| 4 | 3 | 1-2 days | Comprehensive test suite |
| 5 | 4 | 1-2 days | Documentation, examples |
| 6 | 3 | 1 day | Integration testing, verification |
| **Total** | **17 tasks** | **5-7 days** | **Stable CVM adapter** |

---

## Rollout Checklist

Before marking this track complete:
- [ ] All phases completed
- [ ] All tasks closed
- [ ] >80% code coverage achieved
- [ ] All tests passing
- [ ] Documentation complete
- [ ] No known issues or regressions
- [ ] Code review completed
- [ ] Commit messages follow standards
- [ ] Track completion verified

---

## Notes

- This is a refactoring/consolidation track, not a new feature
- Focus on code quality and documentation
- All changes should be backward compatible
- Test thoroughly with real Brazilian market data
- Consider performance impact of market calendar checks
