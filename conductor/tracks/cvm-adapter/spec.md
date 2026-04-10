# Track Specification: Stabilize and Document CVM Market Adapter

**Track ID:** `cvm-adapter`  
**Type:** Enhancement/Consolidation  
**Priority:** High  
**Estimated Effort:** 5-7 days

## Overview

Consolidate recent work on Brazilian market (CVM) adaptation, ensure clean integration with the core TradingAgents framework, improve configuration handling for market-specific parameters, and provide comprehensive documentation for users deploying TradingAgents in the Brazilian market.

## Background

Recent work has adapted TradingAgents to work with the Brazilian market and CVM (Comissão de Valores Mobiliários) regulations:
- Commits: "Adaptação do TradingAgents para o mercado brasileiro (CVM)"
- Commits: "feat: adapta framework para execução completa do TradingAgents com Qwen 3.5 35B"
- Config updates for market-specific behavior

This track will stabilize and formalize that work.

## Problem Statement

The CVM market adapter exists but needs:
1. **Code Quality**: Ensure clean separation of concerns, consistent with framework patterns
2. **Configuration**: Proper market-specific configuration handling
3. **Testing**: Comprehensive test coverage for Brazilian market features
4. **Documentation**: Clear docs for users on how to use TradingAgents with CVM markets
5. **Integration**: Verify seamless integration with multi-LLM support

## Scope

### In Scope
- [ ] Review and refactor existing CVM market adapter code
- [ ] Consolidate market-specific configuration handling
- [ ] Implement comprehensive test suite for CVM market functionality
- [ ] Create documentation for CVM market usage
- [ ] Verify integration with Qwen and other local LLM providers
- [ ] Validate Brazilian stock data sources (B3, CVM data)
- [ ] Implement market hours/trading calendar for Brazilian exchanges

### Out of Scope
- [ ] Real-world trading deployment (research framework only)
- [ ] CVM compliance auditing (responsibility of users)
- [ ] Performance optimization beyond current scope
- [ ] Additional market adapters (beyond Brazilian)

## Acceptance Criteria

### Code Quality
- [ ] All CVM adapter code follows Python Code Style Guide
- [ ] Type hints present on all public functions
- [ ] No hardcoded market-specific values (use configuration)
- [ ] Code duplication minimized
- [ ] Error handling for market data unavailability

### Testing
- [ ] >80% code coverage for CVM adapter code
- [ ] Unit tests for market data fetching
- [ ] Unit tests for market hours/calendar logic
- [ ] Integration tests with sample Brazilian stock data
- [ ] Tests pass with multiple LLM configurations
- [ ] Tests handle API failures gracefully

### Configuration
- [ ] `DEFAULT_CONFIG` includes CVM market parameters
- [ ] Market selection works via configuration (not hardcoded)
- [ ] Configuration validation on startup
- [ ] Clear error messages for invalid market configurations
- [ ] Example configurations for common scenarios

### Documentation
- [ ] README updated with CVM market usage example
- [ ] Docstrings added to all public CVM adapter functions
- [ ] `docs/cvm-market-guide.md` created with:
  - Overview of Brazilian market integration
  - Configuration examples
  - Supported data sources
  - Known limitations
  - Troubleshooting guide
- [ ] Configuration options documented with examples

### Integration & Validation
- [ ] Verify data fetching from B3/CVM sources
- [ ] Test with Qwen local LLM provider
- [ ] Test with OpenAI/Google/Anthropic providers
- [ ] Verify trading calendar matches Brazilian exchange hours
- [ ] Verify no regression in existing functionality

## Technical Details

### Market Data Sources
- **Primary**: yfinance (supports Brazilian stocks via `.SA` suffix)
- **Secondary**: Direct B3 API integration (if available)
- **CVM Data**: News and regulatory announcements

### Trading Calendar
- Brazilian stock exchange hours: 10:00-17:50 BRT
- Trading days: Monday-Friday (excluding holidays)
- Need to implement holiday calendar for Brazilian holidays

### Configuration Example
```python
CVM_MARKET_CONFIG = {
    "market": "brazilan",  # or "us", "global"
    "exchange": "B3",
    "timezone": "America/Sao_Paulo",
    "trading_hours": {
        "open": "10:00",
        "close": "17:50",
        "timezone": "BRT"
    },
    "data_sources": {
        "prices": "yfinance",  # B3 stocks end with .SA
        "news": "cvm_api",
        "fundamentals": "yfinance"
    },
    "broker": "simulated",  # Simulation only
    "currency": "BRL"
}
```

## Dependencies
- yfinance (already in dependencies)
- Python-dateutil for calendar handling
- pytz for timezone handling (already in dependencies)

## Success Metrics

1. **Code Quality**: 100% of CVM adapter code has type hints and docstrings
2. **Testing**: >80% coverage achieved
3. **Documentation**: Users can configure and run TradingAgents for Brazilian market with provided docs
4. **Integration**: Framework passes all tests with CVM configuration
5. **Performance**: Market data fetching performant (<2s per request)

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data source API changes | Document API versions used, add fallback data sources |
| Trading hours edge cases | Comprehensive test cases for holidays, pre/post market |
| LLM provider compatibility | Test explicitly with Qwen, OpenAI, Anthropic |
| Configuration complexity | Start simple, comprehensive examples in docs |

## Timeline

**Phase 1** (Day 1-2): Code review and refactoring
**Phase 2** (Day 2-3): Test suite implementation
**Phase 3** (Day 4-5): Configuration consolidation
**Phase 4** (Day 5-6): Documentation
**Phase 5** (Day 6-7): Integration testing and verification

## Deliverables

1. Refactored CVM market adapter code
2. Comprehensive test suite (>80% coverage)
3. Updated `DEFAULT_CONFIG` with market parameters
4. User documentation (`docs/cvm-market-guide.md`)
5. Updated README with CVM example
6. Configuration validation implementation
7. All tests passing, no regressions
