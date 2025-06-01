# Project Testing Constraints

## Philosophy
**No Mock Libraries** - Do not use mock features of pytest/unittest in Python projects. Mock is banned due to maintenance complexity and testing philosophy.
**End-to-End Always** - Always test end to end using the real functions from the project. If necessary, install a client/server to test what you build live.

