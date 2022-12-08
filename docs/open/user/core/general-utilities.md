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

!!! tip "Break Into Debugger"
    It is possible to have assert macros break into the debugger upon failure. To do that, enable
    the CMake option `LAGRANGE_ASSERT_DEBUG_BREAK` when compiling Lagrange into your project.

## Type Cast

It is often necessary to cast a variable from one type to another. To ensure
such cast is safe, Lagrange provides an explicit casting function:

```c++
#include <lagrange/utils/safe_cast.h>

// Cast variable y into variable x of type `type1`
type1 x = lagrange::safe_cast<type1>(y);
```

!!! note "Implementation Detail"
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

## Disjoint-Set / Union-Find

Lagrange provide a simple [Disjoint-Set][disjoint-sets] data-structure that can be used to implement
algorithms such as Kruskal's minimum spanning tree.

```c++
#include <lagrange/utils/DisjointSets.h>

using Edge = std::array<Index, 2>;

std::vector<Edge> min_spanning_tree(
    Index num_vertices,
    const std::vector<Edge>& sorted_edges)
{
    // Disjoint-sets for efficient union-find operations
    DisjointSets<Index> union_find(num_vertices);
    std::vector<Edge> output_edges;

    // Iterate over all input edges in ascending order
    for (auto [x, y] : sorted_edges) {
        [x, y] = sorted_edges[e];

        // If vertices belong to disconnected unrooted trees,
        // merge them and add edge (x, y) to the solution
        if (union_find.find(x) != union_find.find(y)) {
            output_edges.emplace_back(x, y);
            union_find.merge(x, y);
        }
    }
    return output_edges;
}
```

!!! note "Implementation Detail"
    For simplicity, our Disjoint-Set data structure currently only implements _path compression_,
    but not union by rank.

[disjoint-sets]: ../../../{{ dox_folder }}/classlagrange_1_1_disjoint_sets.html

## BitField

The [BitField][bit-field] class can be used to implement convenient bitwise boolean operations over
an enum type.

```c++
#include <lagrange/utils/BitField.h>
#include <lagrange/Logger.h>

enum Operation : int {
    Translation = (1 << 0),
    Rotation = (1 << 1),
    Scaling = (1 << 2),,
}
BitField<Operation> op;
op.set(Operation::Translation);
op.set(Operation::Scaling);
if (op.test(Operation::Scaling)) {
    lagrange::logger().info("Scaling bit is set");
}
```

[bit-field]: ../../../{{ dox_folder }}/classlagrange_1_1_bit_field.html

## Floating Point Exceptions

On certain platforms, it is possible to trap [floating point
exceptions](https://en.wikipedia.org/wiki/IEEE_754#Exception_handling) using [compiler-specific
functions](https://en.cppreference.com/w/cpp/numeric/fenv). This is useful for debugging purposes,
e.g. to detect when a NaN is emitted during numerical computation.

Lagrange provide a convenient platform-agnostic function called [enable_fpe()][fpe] /
[disable_fpe()][fpe] to enable/disable trapping floating point exceptions. Our implementation
currently supports Linux and macOS. On non-supported platform, calling the function is a no-op.

```c++
#include <lagrange/utils/fpe.h>

void my_main() {
    lagrange::enable_fpe();
    // call problematic operation []...]
    lagrange::disable_fpe();
}
```

!!! tip "Compilation Issues"
    If our implementation of `enable_fpe()` casues compilation issues on your target platform (e.g.
    macOS M1, Emscripten, etc.), it is possible to disable the feature explicitly by setting the
    CMake option `LAGRANGE_DISABLE_FPE=ON`. In this case, calling `enable_fpe()` will do nothing.

[fpe]: ../../../{{ dox_folder }}/group__group-utils-misc.html#ga19b64389774c826a71abae902e0b46b9

## Scope Guard

Sometimes it is necessary to ensure that certain resources are properly deallocated when leaving the
scope of a function. This typically happens when dealing with C API that provide abstract object
handling functions such as:

```c++
struct MyObject;

MyObject * create_object();

void delete_object(MyObject *);
```

To make object deletion exception-safe in C++, one must ensure that the `delete_object()` function
is called even if an exception is raised. One possibility is to use a
[RAII](https://en.cppreference.com/w/cpp/language/raii) class. Lagrange provides a simple
[make_scope_guard()][make-scope-guard] function that wraps an arbitrary callable using RAII:

```c++
#include <lagrange/utils/scope_guard.h>

void my_function() {
    MyObject *obj = create_object();

    // Deferred called to `delete_object()` destructor.
    // Called when `guard` goes out of scope.
    auto guard = lagrange::make_scope_guard([&]( delete_object(obj); ));

    // Use `obj` ...
}
```

This paradigm is also useful when using imperative programming, e.g. when implementing an "editable
state" in an object, and you want to ensure the `begin_edit()` and `end_edit()` methods are always
called together. It can also be use to wrap calls to `glBegin()` and `glEnd()` in OpenGL, ensuring
the state machine stays consistent.

[make-scope-guard]: ../../../{{ dox_folder }}/group__group-utils-misc.html#ga473b5d2b31badd808124196a21ce0b45

## Stack-Allocated Containers

Lagrange provides different implementations of stack-allocated containers. Such containers are
extremely useful when dealing with many small buffers with a known upper-limit size, or at least a
good initial guess. For example if the nodes of a graph have at most 6 neighbors, you can use a
stack-allocated containers to store the neighbor indices. Another example is storing a quad-dominant
mesh, where facets can have a size 3 or 4.

Lagrange currently provide the following implementations:

- **[SmallVector][small-vector]**. An implementation of a `std::vector<>` with a pre-allocated stack
  buffer that grow on the heap beyond the initial upper limit.
- **[StackVector][stack-vector]**. An implementation of a `std::vector<>` with a fixed upper size
  provided at compile-time. Inserting new elements beyond the limit will throw an exception.
- **[StackSet][stack-set]**. An implementation of a `std::set<>` with a fixed upper size provided at
  compile-time. Inserting new elements beyond the limit will throw an exception.

[small-vector]: ../../../{{ dox_folder }}/classlagrange_1_1_small_vector.html
[stack-vector]: ../../../{{ dox_folder }}/structlagrange_1_1_stack_vector.html
[stack-set]: ../../../{{ dox_folder }}/structlagrange_1_1_stack_set.html

## Shared Span

Lagrange's [SurfaceMesh](mesh.md) class relies heavily on a [span<>][span] implementation to provide
bounds-safe view over raw pointers. Since our mesh attribute supports copy-on-write and wrapping of
external buffers, it can be desirable to wrap external buffers as attribute while managing their
lifetime.

To this end, Lagrange implements a [SharedSpan][shared-span] object that offers a bounds-safe view
over a raw pointer, while tracking the actual owner object via a different `std::shared_ptr<>`.

!!! example "Example 1: Buffer Created via a C-style API"

    ```c++
    struct MyMesh {
        std::vector<float> vertices;
        std::vector<uint32_t> facets;
    };

    // Create a new mesh instance
    MyMesh * mesh_new();

    // Free previously allocated mesh instance
    void mesh_free(MyMesh* obj);

    void wrap_mesh(lagrange::SurfaceMesh<float, uint32_t> &mesh)
    {
        // Create vertex buffer via abstract C API
        auto owner_obj = std::shared_ptr<MyObject>(mesh_new(), &mesh_free);

        // Number of vertices is number of coordinates divided by 3
        uint32_t num_vertices = owner_obj->vertices.size() / 3;

        // Create a "view" of the raw vertices pointer while tracking ownership information
        auto vertices_vew = make_shared_span(
            owner_obj,
            owner_obj->vertices.data(),
            owner_obj->vertices.size());

        mesh.wrap_as_vertices(vertices_vew, num_vertices);

        // Wrap facet buffer sharing the same owner object
        uint32_t num_facets = owner_obj->facets.size() / 3;
        auto facets_vew = make_shared_span(
            owner_obj,
            owner_obj->facets.data(),
            owner_obj->facets.size());
        mesh.wrap_as_facets(facets_view, num_facets, 3);
    }
    ```

!!! example "Example 2: Buffer Stored as an Eigen Matrix"

    ```c++
    using RowMatrixXd = Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor>;

    // Moves a N x 3 matrix of vertex positions into a Lagrange SurfaceMesh
    // without copying the underlying buffer
    void wrap_vertices(lagrange::SurfaceMesh32d& mesh, RowMatrixXd&& V)
    {
        // Take ownership of the input matrix V
        auto eigen_matrix = std::make_shared<RowMatrixXd>(std::move(V));

        // Create a safe view of the raw position data
        auto vertices_view =
            lagrange::make_shared_span(eigen_matrix, eigen_matrix->data(), eigen_matrix->size());

        // Wrap raw position data as vertices without any copy
        mesh.wrap_as_vertices(vertices_view, eigen_matrix->rows());
    }
    ```


[span]: ../../../{{ dox_folder }}/group__group-utils-misc.html#ga4afead0b9ccc53fe4fca896787595d26
[shared-span]: ../../../{{ dox_folder }}/classlagrange_1_1_shared_span.html

[range]: ../../../{{ dox_folder }}/group__group-utils-misc.html#ga68084717e646e9a6073e533d0b83a2b7
[spdlog]: https://github.com/gabime/spdlog
[CLI11]: https://github.com/CLIUtils/CLI11
[chrono]: https://en.cppreference.com/w/cpp/chrono
