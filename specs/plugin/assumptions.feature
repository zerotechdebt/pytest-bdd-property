Feature: Assumption Pattern Registry

  Assumptions filter generated inputs. Patterns are registered as
  regex + builder pairs. Step text is matched against patterns to
  produce filter predicates.

  @RID-PLG-ASM-001
  Rule: Registering an assumption pattern makes it parseable
    Scenario: Register and parse a custom assumption
      Given an assumption pattern "^<(\w+)> is positive$" is registered
      When the step "<N> is positive" is parsed as an assumption
      Then an assumption function is returned

  @RID-PLG-ASM-002
  Rule: Unrecognized step text returns null/None
    Scenario: No matching pattern
      When the step "something completely unknown" is parsed as an assumption
      Then no assumption is returned

  @RID-PLG-ASM-003
  Rule: All 12 built-in assumption patterns are registered at import time
    Scenario: Built-in patterns cover equality, comparison, emptiness, length, containment, type checks
      When the assumption patterns are listed
      Then at least 12 patterns are registered

  @RID-PLG-ASM-004
  Rule: Emptiness assumptions generalize beyond strings to arrays and nulls
    Scenario: Arrays and nulls are handled by is empty and is not empty
      Given the assumption "<X> is not empty" is parsed
      Then it accepts non-empty arrays and rejects empty arrays and nulls
      Given the assumption "<X> is empty" is parsed
      Then it accepts empty arrays and nulls and rejects non-empty arrays
