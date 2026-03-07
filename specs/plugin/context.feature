Feature: Property Context Lifecycle

  Each @property-based scenario gets a fresh PropertyContext that
  accumulates strategies, assumptions, actions, and assertions
  during Phase 1.

  @RID-PLG-CTX-001
  Rule: A fresh context has empty strategies, assumptions, actions, and assertions
    Scenario: New context is empty
      Given a new property context is created
      Then it has no strategies
      And it has no assumptions
      And it has no actions
      And it has no assertions

  @RID-PLG-CTX-002
  Rule: Context is created on demand for property-based scenarios
    Scenario: Context created when first accessed
      Given a property-based scenario is running
      When a strategy is registered via a Given step
      Then a context exists with that strategy

  @RID-PLG-CTX-003
  Rule: Context is reset between scenarios
    Scenario: Previous context does not leak
      Given a property-based scenario has completed
      When a new property-based scenario starts
      Then the context is fresh and empty

  @RID-PLG-CTX-004
  Rule: Non-property scenarios have no context
    Scenario: Regular scenario has no property context
      Given a scenario without @property-based tag
      Then no property context exists
