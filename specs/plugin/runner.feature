Feature: Property Test Execution (Phase 2)

  After all steps run, the runner builds a composite strategy
  from all registered strategies, applies assumptions, executes
  actions, and checks assertions — many times with generated inputs.

  @RID-PLG-RUN-001
  Rule: The runner builds a composite strategy from all registered variable strategies
    Scenario: Composite strategy
      Given strategies for "P" (text) and "N" (integer) are registered
      When the property test is executed
      Then generated values contain keys "P" and "N"

  @RID-PLG-RUN-002
  Rule: Assumptions filter out invalid inputs before actions execute
    Scenario: Assumption filtering
      Given a strategy for "N" (integer) and assumption "N > 0"
      When the property test is executed
      Then all generated N values are positive

  @RID-PLG-RUN-003
  Rule: Actions execute in registration order
    Scenario: Action ordering
      Given two actions registered in order A then B
      When the property test is executed
      Then A runs before B on each generated input

  @RID-PLG-RUN-004
  Rule: Assertions execute after all actions
    Scenario: Assertion after action
      Given an action that stores a result and an assertion that reads it
      When the property test is executed
      Then the assertion has access to the action's result

  @RID-PLG-RUN-005
  Rule: A failing assertion triggers shrinking to a minimal counterexample
    Scenario: Shrinking on failure
      Given a property that fails for some inputs
      When the property test is executed
      Then the error contains a shrunk counterexample

  @RID-PLG-RUN-006
  Rule: No registered strategies raises an error
    Scenario: Empty strategies
      Given no strategies are registered
      When the property test is attempted
      Then an error is raised about missing strategies

  @RID-PLG-RUN-007
  Rule: The runner applies parsed settings for numRuns and seed
    Scenario: Settings control execution
      Given a strategy and settings with numRuns=7 and seed=42
      When the property test is executed
      Then the action runs exactly 7 times
