# Contributor Guidelines

So, you want to contribute code to Lagrange? Great! Here are a few bits of information and tips:

{% if is_corp %}

{% include 'corp/dev/contribute.md' %}

{% else %}

## Checklist

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the Lagrange repository in
   GitHub.
2. Check our [code of conduct](https://github.com/adobe/lagrange/blob/main/CODE_OF_CONDUCT.md).
3. Check our [code style](code-style.md) + make sure .clang-format is applied.
4. Run [unit tests](unit-tests.md) + upload your own unit test data to our [test data
   repository](https://github.com/adobe/lagrange-test-data).
5. Push your work to a new branch in your own fork.
6. Open a [pull request](https://github.com/adobe/lagrange/pulls) on github and give it a readable
   title.

{% endif %}

## Coding Style And Conventions

Please check our [coding style guide](code-style.md).

Unfortunately, some files in Lagrange may not be following the above guide. If you change those
files, feel free to fix them accordingly, or respect the existing style. Do not output a file with
inconsistent code style.

Try to write code that compiles without compiler warnings. Follow the general [design
principles](../index.md). Check the [mesh class](../user/core/mesh.md) for common functionality, and
use similar template and type names. Use [utility functions](../user/core/general-utilities.md)
for common functionalities such as logging, timing, casting, and optionally ranges.

## Creating New Files

Please name your new file consistently with the functionality implemented inside. Use lowercase
`compute_something.h` for functions and Uppercase `SomeNewType.h` for types (classes). If your file
contains more than one function, please document an overview of the contents at the top. After
creating the new file, you may need to add it to the CMake build system, and run `cmake ..` again.

## Adding A New Module

It is possible for your contribution to justify the creation of a new Lagrange module. This is
especially encouraged for large contributions, or those that require external dependencies.

To create a new module, pick an expressive and concise name, and use it consistently across CMake,
folders, and C++ namespaces. Use existing modules as reference. You should add your new module to
the `modules` directory. Each module has similar subdirectory setup:

* `CMakeLists.cmake` to specify how to build the module.
* `include/lagrange/<module_name>/` contains the header files.
* `src/` contains the source codes.
* `tests/` contains unit tests specific to this module.
* `performance/` contains performance tests.
* `examples/` contains stand alone examples illustrating typical usage.

## Adding New Third-Party Code

{% if is_corp %}

!!! important "License Considerations"
    Make sure the third-party code uses an acceptable license as defined by the [Open Source
    Guidelines](https://wiki.corp.adobe.com/display/legalwiki/Open+Source+Guidelines+for+use+in+Adobe+Products+and+Services).

{% else %}

!!! important "License Considerations"
    Make sure the third-party code uses an acceptable license. Please open an issue to discuss the
    matter if you are unsure about it.

{% endif %}

- When adding a new third-party dependency:
    1. Place the corresponding `foo.cmake` file in `cmake/recipes` following existing models.
    2. Update the `ALL_THIRD_PARTIES` in `scripts/lagrange_ci/third_parties.py` accordingly.
- When adding new bundled code directly into the Lagrange repository:
    1. Make sure the file header gives proper attribution to the source code origin.
    2. Update the `NOTICE_LIST` in `scripts/lagrange_ci/notice.py`.

## Unit Testing

<!-- todo: a wiki page on why tests are awesome? Pretty sure we have material. @qzhou? -->
Please check our [unit tests guide](unit-tests.md). Tests are awesome and highly encouraged. You can
add your unit tests in `modules/<module_name>/tests`.

While developing your code, you can run only your specific test case(s) by passing the name(s) as
argument to the test executable. You can also tag your new tests according to your new feature, and
run all of them.

```sh
./tests/test_lagrange_core "SafeCast"  # Run SafeCast test case.
./tests/test_lagrange_core "[mesh]"  # Run all test cases tagged with "[mesh]"
```

In case you also develop a small application that uses your new feature, feel free to include that
in `modules/<module_name>/examples`.

!!! important "Legacy Performance Tests"
    Some modules have a `modules/<module_name>/performance` subfolder containing some "performance"
    tests. This is legacy code. New benchmarking tests should be written along with other unit
    tests, use [Catch2's benchmarking
    framework](https://github.com/catchorg/Catch2/blob/devel/docs/benchmarks.md), and be tagged as
    `[!benchmark]`.

{% if is_corp %}

## Pull Requests And Jenkins

You can create a pull request (PR) at any time from the GitHub web interface. While a PR is open,
Jenkins will try to build your branch at every commit on different platforms (Windows, OSX, Unix).

When your code is ready, request a review, and stay updated for any feedback.

{% else %}

## Pull Requests

You can create a pull request (PR) at any time from the GitHub web interface. <!-- While a PR is open, GitHub Actions will try to build your branch at every commit on different platforms (Windows, OSX, Unix). -->
When your code is ready, request a review, and stay updated for any feedback.

{% endif %}
