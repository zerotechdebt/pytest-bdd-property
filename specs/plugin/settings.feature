Feature: Settings Parsing from Tags

  Configuration tags on @property-based scenarios control
  execution parameters.

  @RID-PLG-SET-001
  Rule: @num-runs:N sets the number of generated examples
    Scenario: Custom run count
      Given a scenario tagged @property-based and @num-runs:50
      When settings are parsed from tags
      Then num_runs is 50

  @RID-PLG-SET-002
  Rule: @seed:N sets a fixed random seed
    Scenario: Fixed seed
      Given a scenario tagged @property-based and @seed:42
      When settings are parsed from tags
      Then seed is 42

  @RID-PLG-SET-003
  Rule: @verbose enables verbose output
    Scenario: Verbose mode
      Given a scenario tagged @property-based and @verbose
      When settings are parsed from tags
      Then verbose is true

  @RID-PLG-SET-004
  Rule: Unrecognized tags are ignored
    Scenario: Unknown tag
      Given a scenario tagged @property-based and @unknown-tag
      When settings are parsed from tags
      Then settings contain only default values
