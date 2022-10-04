<!-- $ignore -->

# General Utility Functions

## Logging

Lagrange uses [spdlog] for logging purposes. Spdlog provides feature-rich formatting via the
excellent [fmt](https://github.com/fmtlib/fmt) library. This provides several advantages over a
traditional `std::cout` messaging:

- Python-like formatting syntax improves code readability
- 6 levels of logging: trace, debug, info, warn, error, critical
- Fast, thread-safe formatting
- Multiple sinks (file, stdout, etc.)

The default Lagrange logger can be accessed as follows:

```c++
#include <lagrange/Logger.h>

lagrange::logger().debug("This mesh has {} vertices and {} facets", v, f);
```

To control the logging level, or set additional sinks (e.g. to write logs to a file), please read
the [spdlog] documentation.

A common pattern we use in example applications is to set the logging level/sink via command-line
arguments. E.g. using [CLI11] to parse cli args:

```c++
struct
{
    std::string log_file;
    int log_level = 2;
} args;

// Parse command-line args with CLI11
CLI::App app{argv[0]};
app.option_defaults()->always_capture_default();
app.add_flag("-q,--quiet", args.quiet, "Hide logger on stdout.");
app.add_option("-l,--level", args.log_level, "Log level (0 = most verbose, 6 = off).");
app.add_option("-f,--log-file", args.log_file, "Log file.");
CLI11_PARSE(app, argc, argv)

if (args.quiet) {
    // Hide stdout default sink
    lagrange::logger().sinks().clear();
}
if (!args.log_file.empty()) {
    // Add a new file sink
    lagrange::logger().sinks().emplace_back(
        std::make_shared<spdlog::sinks::basic_file_sink_mt>(args.log_file, true));
}

// Set log level
args.log_level = std::max(0, std::min(6, args.log_level));
spdlog::set_level(static_cast<spdlog::level::level_enum>(args.log_level));
```

## Timing

Lagrange provides handy timing functions based on modern C++'s [chrono] package.
Here is an example use case:

```c++
#include <lagrange/utils/timing.h>

auto start_time = lagrange::get_timestamp();
...
auto finish_time = lagrange::get_timestamp();

auto duration = lagrange::timestamp_diff_in_seconds(start_time, finish_time);
lagrange::logger().info("Duration: {}s", duration);
```

## Assertion

Lagrange provide two types of assertion macros:

- **Runtime assertions**, using `la_runtime_assert().` Those are used to check the validity of user
  inputs as a pre-condition to a function. For example, providing a function with an empty, or a
  mesh with incorrect dimension, could result in such an assertion being raised. A runtime assert is
  executed even in Release configuration, and indicates a problem with the function input.

- **Debug assertions** using `la_debug_assert()`. Those are only checked in debug code (macro
  `NDEBUG` is undefined). A debug assert is used to check internal code validity, and should _not_
  be triggered under any circumstance by client code. A failed debug assert indicates an error in
  the programmer's code, and should be fixed accordingly.

!!! info "Usage In Expressions"
    Our assert macros behave as functions, meaning they expand to a `void` expression and can be
    used in an expression such as `y = (la_debug_assert(true), x)`.

Our assertion macros can take either 1 or 2 arguments, the second argument being an optional error
message. To conveniently format assertion messages with a printf-like syntax, use `fmt::format`:

```c++
#include <lagrange/utils/assert.h>
#include <spdlog/fmt/fmt.h>

la_debug_assert(x == 3);
la_debug_assert(x == 3, "Error message");
la_debug_assert(x == 3, fmt::format("Incorrect value of x: {}", x));
```

It is possible to have assert macros break into the debugger upon failure. To do that, enable the
CMake option `LAGRANGE_ASSERT_DEBUG_BREAK` when compiling Lagrange into your project.


## Type Cast

It is often necessary to cast a variable from one type to another.  To ensure
such cast is safe, Lagrange provides an explicit casting function:

```c++
#include <lagrange/utils/safe_cast.h>

// Cast variable y into variable x of type `type1`
type1 x = lagrange::safe_cast<type1>(y);
```


!!! note "Implementation Details"
    `safe_cast` checks for type compatibility, sign consistency and truncation error.  We
    recommended to use code that avoids casting in the first place.

## Pointer Type Conversion

It often necessary to convert a `std::unique_ptr` to `std::shared_ptr`.
Lagrange provide a handy function that avoid repeated type specification:

```c++
#include <lagrange/common.h>

std::unqiue_ptr<T> unique_val = ...;
auto shared_val == lagrange::to_shared_ptr(unique_val);
assert(unique_val == nullptr);
assert(shared_val.use_count() == 1);
```

## Range

Lagrange provides a handy [`range()`][range] function to enable a python-like range-based
for loop:

```c++
#include <lagrange/range.h>

for (auto i : lagrange::range(num_vertices)) {
    // i goes from 0 to num_vertices-1
}
```

The advantage of using `range()` is that the type of the index variable `i` is
automatically inferred from the type of `num_vertices`.  This reduces
the amount of unnecessary implicit casts and compiler warnings.

Lagrange also provide `range_sparse()` to loop through an active subset of the
range:

```c++
#include <lagrange/range.h>

std::vector<Index> active_set;

// Populate active_set... (optional)

for (auto i : lagrange::range_sparse(N, active_set)) {
    // i will loop through only the active entries.
}
```

The iterator behaves as follows:
- If `active_set` is empty, `range_sparse(N, active_set)` will loop from 0 to `N` (same behavior as
  `range(N)`).
- However, if `active_set` is non-empty, `range_sparse(N, active_set)` will loop through the entries
  of `active_set`.


[range]: ../../../{{ dox_folder }}/group__group-utils-misc.html#ga68084717e646e9a6073e533d0b83a2b7
[spdlog]: https://github.com/gabime/spdlog
[CLI11]: https://github.com/CLIUtils/CLI11
[chrono]: https://en.cppreference.com/w/cpp/chrono
