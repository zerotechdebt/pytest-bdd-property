Feature: Strategy Registry

  The strategy registry maps natural-language names to input generators.
  Names are case-insensitive. Unknown names produce helpful errors.

  @RID-PLG-REG-001
  Rule: Registering a strategy makes it resolvable by name
    Scenario: Register and resolve a custom strategy
      Given a strategy "valid email" is registered
      When "valid email" is resolved
      Then a strategy is returned

  @RID-PLG-REG-002
  Rule: Strategy names are case-insensitive
    Scenario: Resolve with different casing
      Given a strategy "Valid Email" is registered
      When "valid email" is resolved
      Then a strategy is returned

  @RID-PLG-REG-003
  Rule: Re-registering a name overwrites the previous strategy
    Scenario: Overwrite existing strategy
      Given a strategy "text" is registered with a custom factory
      When "text" is resolved
      Then the custom factory is used

  @RID-PLG-REG-004
  Rule: Resolving an unknown name throws with available strategies listed
    Scenario: Unknown strategy name
      When "nonexistent-type" is resolved
      Then an error is raised containing "Unknown strategy"
      And the error lists available strategy names

  @RID-PLG-REG-005
  Rule: All 16 built-in strategies are registered at import time
    Scenario: List built-in strategies
      When the strategy list is retrieved
      Then it contains at least 16 entries
      And it includes "text", "integer", "email", "uuid", "date"
