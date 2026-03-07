Feature: Step Dispatch

  The plugin intercepts Given/When/Then steps during Phase 1.
  Given steps bind strategies or register assumptions.
  When/Then steps register action/assertion callbacks.
  Steps in non-property scenarios are ignored.

  @RID-PLG-DISPATCH-001
  Rule: "any <type> <var>" Given steps bind a strategy to the variable
    Scenario: Strategy binding
      Given a property-based scenario is running
      When the Given step "any text <P>" is processed
      Then variable "P" has a strategy bound

  @RID-PLG-DISPATCH-002
  Rule: Assumption-shaped Given steps register an assumption
    Scenario: Assumption registration
      Given a property-based scenario is running
      When the Given step "<P> is not equal to <Q>" is processed
      Then an assumption is registered on the context

  @RID-PLG-DISPATCH-003
  Rule: Steps in non-property scenarios are skipped
    Scenario: Non-property scenario
      Given a scenario without @property-based tag
      When the Given step "any text <P>" is processed
      Then the step is not handled

  @RID-PLG-DISPATCH-004
  Rule: When steps are dispatched to property_when pattern matching
    Scenario: When dispatch
      Given a property-based scenario with a registered property_when pattern
      When a matching When step is processed
      Then an action is registered on the context

  @RID-PLG-DISPATCH-005
  Rule: Then steps are dispatched to property_then pattern matching
    Scenario: Then dispatch
      Given a property-based scenario with a registered property_then pattern
      When a matching Then step is processed
      Then an assertion is registered on the context
