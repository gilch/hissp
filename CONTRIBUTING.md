## Contributing
There are many ways to contribute to an open-source project,
even without writing code.

Questions are allowed in the Discussions section.
They help illustrate deficiencies in the documentation,
but do check there first!
(Discussion topics in the issue tracker will be moved to Discussions.)
We also have a chat room.

Bug reports are welcome in the issue tracker.

PRs to help fix issues, improve documentation,
structure, or compatibility will also be considered.

### Pull Requests
PRs must be aligned with the philosophy and goals of the project to be
considered for inclusion.

PRs do not have to be perfect to be submitted,
but must be approved by the owner before they are merged.
Small, focused changes are more likely to be reviewed.

Changes to the source code must be properly formatted and have full test
coverage before the PR can be accepted.
Manual tests may suffice for configuration files.
The Python source uses Black formatting.
Disable this using `# fmt: skip` tags or `# fmt: off` regions (as appropriate) 
for "readerless mode" Hissp snippets
which should be formatted Lisp-style (See the style guide.)
or anywhere the extra effort of manual formatting is worth it.
In readerless mode, Hissp tuples shall always include the trailing `,`.
Regular expression raw strings use a lower-case `r`,
but other raw strings use an upper-case `R`.
Try to follow the established style in any source files,
and otherwise follow PEP 8 even when Black has no opinion.
The .lissp source uses the Hissp style guide for formatting.
It must also pass Parlinter.
The owner is the final arbiter of style.

Documentation is expected to have correct (American English) spelling
and grammar. All Doctests must pass.

You can use pytest to run unittests and doctests at the same time.
Make sure you install the dev requirements first.
Hissp proper has no dependencies, but its test suite does.
```
$ pip install -r requirements-dev.txt
```
See the .github/ folder for the full test pipeline.

We do not commit directly to master.
We merge to master without squashing.
Commit structure is important for git blame and git bisect.
Tests should pass after each commit.
Commits must be small and focused enough to be reviewable;
PRs can't be accepted on faith.
You may be asked to restructure your commits during the PR process.
This may require a force-push to your PR branch.
We prefer a rebase on master to a backwards merge in order to maintain a linear commit history.
