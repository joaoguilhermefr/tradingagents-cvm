# Implementation Plan: Agent Data Sources & Indicator Computation Refactoring

## Phase 1: Planning & Analysis
- [ ] Task: Review current agent implementation and data flows
  - [ ] Analyze sentiment analyst usage and dependencies
  - [ ] Map news analyst data requirements
  - [ ] Study technical indicator calculation approach
  - [ ] Review fundamental analyst structure
  - [ ] Document current data sources and gaps

- [ ] Task: Set up development environment
  - [ ] Create feature branch
  - [ ] Verify finbr library availability and API
  - [ ] Identify material_facts.py patterns to adopt
  - [ ] Review financial_analyst.py indicator patterns

## Phase 2: Test Definition (TDD - Red Phase)
- [ ] Task: Write tests for disabled Sentiment Analyst
  - [ ] Test sentiment analyst removal from agent graph
  - [ ] Test trader agent without sentiment input
  - [ ] Test error handling for missing sentiment data

- [ ] Task: Write tests for News Analyst enhancement
  - [ ] Test news data retrieval from sources
  - [ ] Test material facts extraction
  - [ ] Test error handling for missing news
  - [ ] Test news data structure and validation

- [ ] Task: Write tests for Market/Technical Analyst
  - [ ] Test finbr price data retrieval
  - [ ] Test opening/closing price fetching
  - [ ] Test technical indicator computation (MACD, RSI)
  - [ ] Test edge cases (missing prices, insufficient data)
  - [ ] Test indicator accuracy against known values

- [ ] Task: Write tests for Fundamental Analyst
  - [ ] Test indicator extraction from financial data
  - [ ] Test _compute_indicators() method
  - [ ] Test distinction between extracted vs computed indicators
  - [ ] Test edge cases and missing data

- [ ] Task: Write integration tests
  - [ ] Test full agent workflow with new data sources
  - [ ] Test agent interactions with new data

## Phase 3: Implementation (TDD - Green & Refactor)
- [ ] Task: Disable Sentiment Analyst
  - [ ] Remove or comment out sentiment analyst from agent imports
  - [ ] Update agent graph to exclude sentiment analyst node
  - [ ] Update trader agent to not depend on sentiment analysis
  - [ ] Pass tests: sentiment analyst removal

- [ ] Task: Implement News Analyst enhancement
  - [ ] Create news data retrieval function (material_facts pattern)
  - [ ] Implement news source integration
  - [ ] Add news data validation and structuring
  - [ ] Update news analyst to use new data source
  - [ ] Pass tests: news data retrieval and processing

- [ ] Task: Implement Market/Technical Analyst
  - [ ] Add finbr library integration
  - [ ] Implement price data retrieval function
  - [ ] Implement technical indicator computation
  - [ ] Update market analyst to use computed indicators
  - [ ] Pass tests: price fetching and indicator computation

- [ ] Task: Enhance Fundamental Analyst
  - [ ] Implement indicator extraction logic
  - [ ] Implement _compute_indicators() method
  - [ ] Update fundamental analyst with new indicators
  - [ ] Pass tests: indicator extraction and computation

- [ ] Task: Code formatting and quality
  - [ ] Format code with Black
  - [ ] Sort imports with isort
  - [ ] Add type hints where missing
  - [ ] Review for SOLID principles

## Phase 4: Integration Testing
- [ ] Task: Run full test suite
  - [ ] Execute: `pytest tests/`
  - [ ] Verify all tests pass

- [ ] Task: Verify code coverage
  - [ ] Execute: `pytest --cov=tradingagents tests/`
  - [ ] Ensure coverage >80% for modified code
  - [ ] Document coverage report

- [ ] Task: Test with real data (if applicable)
  - [ ] Test news analyst with actual market news
  - [ ] Test market analyst with finbr price data
  - [ ] Test fundamental analyst with real financial data

- [ ] Task: Verify no regressions
  - [ ] Test other analyst agents still work
  - [ ] Test trader and portfolio manager integration

## Phase 5: Documentation & Analysis
- [ ] Task: Generate llm_proposal.md report
  - [ ] Analyze changes in data availability
  - [ ] Identify LLM prompts that need updates
  - [ ] Document recommendations for future prompt modifications
  - [ ] Note impact on agent decisions and outputs

- [ ] Task: Update inline documentation
  - [ ] Add/update docstrings for modified agents
  - [ ] Add comments for complex logic (indicator computation)
  - [ ] Update class documentation

- [ ] Task: Update project documentation
  - [ ] Update README if user-facing changes
  - [ ] Document new data source dependencies (finbr)
  - [ ] Document news source integration

## Phase 6: Code Quality Review
- [ ] Task: Final code review
  - [ ] Verify all tests pass
  - [ ] Confirm coverage >80%
  - [ ] Check code formatting (Black, isort)
  - [ ] Review commit messages follow convention
  - [ ] Verify no hardcoded values
  - [ ] Check error handling comprehensive

- [ ] Task: Conductor - Phase Completion Verification (Phase 3-6)
  - [ ] Verify all code changes committed
  - [ ] Confirm test coverage metrics
  - [ ] Review all acceptance criteria met
  - [ ] Document any known limitations

## Phase 7: Git & PR
- [ ] Task: Commit implementation changes
  - [ ] Stage modified files
  - [ ] Commit with message: `refactor(agents): enhance data sources and indicator computation`
  - [ ] Include detailed commit body with changes

- [ ] Task: Create Pull Request
  - [ ] Push feature branch
  - [ ] Create PR against main branch
  - [ ] Add PR description referencing spec.md
  - [ ] Link to llm_proposal.md in PR
