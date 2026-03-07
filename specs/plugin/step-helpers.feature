Feature: Property Step Helpers

  property_when and property_then register Phase 2 callbacks.
  During Phase 1, they capture the step's regex groups and store
  a closure. During Phase 2, the closure is called with generated values.

  @RID-PLG-HELP-001
  Rule: property_when registers an action callback on the context
    Scenario: When step is registered as action
      Given a property-based scenario is running
      When a property_when step matches "<P> is hashed producing <H>"
      Then the context has one action registered

  @RID-PLG-HELP-002
  Rule: property_then registers an assertion callback on the context
    Scenario: Then step is registered as assertion
      Given a property-based scenario is running
      When a property_then step matches "<P> verifies against <H>"
      Then the context has one assertion registered

  @RID-PLG-HELP-003
  Rule: Regex captures are passed to the callback during Phase 2
    Scenario: Captures are forwarded
      Given a property_when pattern "<(\w+)> produces <(\w+)>"
      And a step matching "<X> produces <Y>"
      When the action is executed with generated values
      Then the callback receives captures "X" and "Y"

  @RID-PLG-HELP-004
  Rule: Unmatched step text returns no match
    Scenario: No matching when pattern
      When "unrelated step text" is matched against when patterns
      Then no match is returned
