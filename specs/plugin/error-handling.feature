Feature: Error Handling

  The plugin produces clear error messages for common mistakes.

  @RID-PLG-ERR-001
  Rule: Using "Given any <type> <var>" outside @property-based raises an error
    Scenario: Strategy step in wrong context
      Given a scenario without @property-based tag
      When "Given any text <P>" is executed
      Then an error is raised about @property-based requirement

  @RID-PLG-ERR-002
  Rule: Unknown strategy name in a Given step raises an error listing available strategies
    Scenario: Unknown strategy in step
      Given a property-based scenario
      When "Given any bogus-type <P>" is executed
      Then an error is raised listing available strategies

  @RID-PLG-ERR-003
  Rule: Unrecognized assumption pattern raises an error with guidance
    Scenario: Unknown assumption
      Given a property-based scenario
      When an unrecognized assumption step is processed
      Then an error is raised suggesting registerAssumption

  @RID-PLG-ERR-004
  Rule: property_when/property_then steps outside @property-based raise an error
    Scenario: Property step in wrong context
      Given a scenario without @property-based tag
      When a property_when step is executed
      Then an error is raised about @property-based requirement
