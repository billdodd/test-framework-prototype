
# Test Framework Prototype

A prototype of a test framework that will look for test cases in a directory structure and execute them.
By default it will look in the current working directory.

For this prototype framework, is is assumed the top-level subdirectories represent categories of test cases
like `functional_tests`, `perf_tests`, `interop_tests`, etc. In each of these category subdirectories will
be a second level of subdirectories. Each of these subdirectories will hold one test case to be executed by
the test framework.

