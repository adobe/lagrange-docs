# Tips To Speed Up Compilation Times

If your hand has reached too deep into the depth of C++ template meta-programming and header-only
libraries, you might find yourself in a hot mess of slow-compiling projects and long wait-time
between recompilations.

![](img/xkcd_compiling.png)

Unfortunately, it is very easy to shoot oneself in the foot and blow up compilation times in a C++
project. In this page we will discuss various ways to alleviate the problem.

## Placebo Solutions

These are some "simple" solutions we can use to treat the symptoms (slow compile times) without
addressing the root cause (code architecture). Pre-compiled headers are pretty much a no-brainer to
use with CMake, and may or may not provide some speedup in your project. On Windows, many people use
[IncrediBuild](https://www.incredibuild.com/) for distributed compilation/caching to dramatically
improve compilation performance. On Linux and macOS, you can use [ccache](https://ccache.dev/) for
to improve the performance of repeated builds. Combined with a shared cache database stored in a
Redis server, this will provide additional performance (e.g. in a Jenkins build cluster).
[sccache](https://github.com/mozilla/sccache) is an alternative to ccache that also works on Windows
and support cloud storage. Finally, for distributed compilation on Linux, you can also look into
[icecream](https://github.com/icecc/icecream).

### Use Pre-Compiled Headers

The basic CMake file to enable pre-compiled headers for your project look like this:

```cmake
# We use an interface target to define commonly used pre-compiled headers
add_library(mylib_pch INTERFACE)

# Always define an alias in the form foo::bar to prevent silly CMake errors
add_library(mylib::pch ALIAS mylib_pch)

# Define commonly used headers here
target_precompile_headers(mylib_pch INTERFACE
    # C++ headers
    <algorithm>
    <chrono>
    <functional>

    # Third party libraries
    <Eigen/Core>

    # Your own library headers
    <mylib/common.h>
    <mylib/Mesh.h>
    <mylib/logger.h>
)

# Reuse the same pre-compiled headers for both lib, executable and unit tests
# (but do not make it a PUBLIC dependency of `mylib`).
target_link_libraries(mylib PRIVATE mylib::pch)
target_link_libraries(myexecutable PRIVATE mylib::pch)
```

!!! tip "Choice of Precompiled Headers"
    You want to add headers that are used often in the project, ideally in at least a third of the
    compilation units. Avoid adding a header to PCH if you are actively working on it.

And that's it! Please consult the official documentation of the
[target_precompile_headers()](https://cmake.org/cmake/help/v3.18/command/target_precompile_headers.html)
function for more information. For example, one could use the `REUSE_FROM` syntax to reuse a list of
pre-compiled headers from one target to the next, rather than using an interface target for this
purpose.

{% if is_corp %}
{% include 'corp/dev/incredibuild.md' %}
{% endif %}

### Using ccache

Ccache can be used to speed up compilation on macOS and Linux. There are similar tools that also
work on Windows, such as [sscache](https://github.com/mozilla/sccache) (developed by Mozilla).

First, make sure you set a cache size large enough to accommodate your C++ projects:
```bash
ccache -M 100G # set max cache size
ccache -s # show stats
```

To enable ccache in a CMake project, simply set the `CMAKE_CXX_COMPILER_LAUNCHER` variable to the
ccache executable. This simple CMake snippet will work on machines with and without ccache
installed:

```cmake
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(CMAKE_C_COMPILER_LAUNCHER   ${CCACHE_PROGRAM})
    set(CMAKE_CXX_COMPILER_LAUNCHER ${CCACHE_PROGRAM})
endif()
```

Without any additional settings however, it is likely that you will not have as many cache hits as
you would like. Here are some important settings to experiment with:

- **`CCACHE_BASEDIR`**: Should be set to either `${CMAKE_BINARY_DIR}` or `${CMAKE_SOURCE_DIR}`.
- **`CCACHE_SLOPPINESS`**: When using pre-compiled headers, it is important to define this to
  `pch_defines,time_macros`. Other settings may improve cache hit performance, such as
  `include_file_mtime`.
- **`CCACHE_PREFIX`**: Should be set when combining ccache with another compiler wrapper (such as
  distcc or icecc for distributed compilation, e.g. `CCACHE_PREFIX=icecc`).

To set those options from your CMake project, you can use the following code snippet:

```cmake
find_program(CCACHE_PROGRAM ccache)
if(CCACHE_PROGRAM)
    set(ccacheEnv
        CCACHE_BASEDIR=${CMAKE_BINARY_DIR}
        CCACHE_SLOPPINESS=clang_index_store,include_file_ctime,include_file_mtime,locale,pch_defines,time_macros
    )
    foreach(lang IN ITEMS C CXX CUDA)
        set(CMAKE_${lang}_COMPILER_LAUNCHER
            ${CMAKE_COMMAND} -E env ${ccacheEnv} ${CCACHE_PROGRAM}
            PARENT_SCOPE
        )
    endforeach()
endif()
```

## Real Solutions

!!! tip "Profile Compilation Times First!"
    Before going head-over-heel and refactor all your code, it is essential that you run some simple
    [profiling tools](compilation-profiling.md) to help you analyze what parts of your project are
    slow to compile.

### Accepting Trade-Offs

To *really* reduce compile times in a C++ project, we need to re-think its architecture and accept
trade-offs. Why are C++ projects slow to compile in the first place? In my experience the main
culprit is often 1) long header parsing time and 2) long codegen time for templated code.

The C++ syntax is incredibly complicated, and after pre-processor STL headers can expand to
thousands of lines of code. Compilers need to work extra hard to parse the language correctly, a
phenomenon that does not improve with new versions of the C++ standard.

Secondly, templated code require the compiler to generate code at each location where a templated
function is used. In a project where everything is templated, deeply nested calls to templated
functions means that the compiler will basically have to compile the whole project for each
translation unit. This kinda defeats the purpose of separating a project in [single compilation
units](https://en.wikipedia.org/wiki/Single_Compilation_Unit) in the first place. Because templated
code is usually header-only, pulling a complicated templated function will pull a lot of dependent
headers, which will need to be parsed, and compiled, etc. The result is a big quagmire of header
files that the compiler needs to go through every time, which leads to tremendously slow compilation
times.

To remedy this, one needs to find **compromise**, and refactor your code accordingly:

1. Do you _need_ to support generic templated types, or do you only need to support a limited number
   of instantiations? E.g. `float` and `double`, or dimensions `2` and `3`?
2. Can you get away with runtime polymorphism (virtual methods, function pointers, etc.) instead of
   compile time polymorphism (templates)? Yes there is an small overhead, but your development time
   might be more valuable than the incurred performance cost. Most of the time, I find that if you
   really need to support a generic type, a virtual class will do just fine.

### Explicit Template Instantiation

The first step to sanitize a C++ project slowed down by expensive templates is to get rid of them.
Seriously. Do not use templates unless you have to.

If you absolutely need do use templates, consider the following:

1. If you only need to support a limited number of types, use explicit template instantiation.
2. Write separate files for function declaration and definition, just like you would for a regular
   C++ function.

#### Before

=== "sum.h"

    ```c++
    #pragma once

    #include <expensive_operation> // Expensive header to parse

    template <typename Scalar>
    Scalar sum(const std::vector<Scalar> &pts) {
        Scalar x = 0;
        for (size_t i = 0; i < pts.size(); ++i) {
            x += expensive_operation(pts[i]);
        }
        return x;
    }
    ```

=== "main.cpp"

    ```c++
    // This will pull other headers, such as `expensive_operation`
    #include "sum.h"

    int main(void) {
        std::vector<float> pts = {0, 1, 2, 3};
        sum(pts);
        return 0;
    }
    ```

#### After

=== "sum.h"

    ```c++
    #pragma once

    template <typename Scalar>
    Scalar sum(const std::vector<Scalar> &pts);
    ```

=== "sum.cpp"

    ```c++
    #include "sum.h"

    // Now `expensive_operation` is safely hidden inside the .cpp
    #include <expensive_operation>

    template <typename Scalar>
    Scalar sum(const std::vector<Scalar> &pts) {
        Scalar x = 0;
        for (size_t i = 0; i < pts.size(); ++i) {
            x += expensive_operation(pts[i]);
        }
        return x;
    }

    // Explicit template instantiation
    template float sum(const std::vector<float> &pts);
    template double sum(const std::vector<double> &pts);
    ```

=== "main.cpp"

    ```c++
    // Now this header is cheap to parse
    #include "sum.h"

    int main(void) {
        std::vector<float> pts = {0, 1, 2, 3};
        sum(pts);
        return 0;
    }
    ```

To avoid repeating explicit template instantiations for various types, we can use a [cool macro
trick](#x-macro-trick-for-explicit-instantiations) described at the end of this page.

!!! warning "Definitions In Header Files"
    One could also envision using separate header files for the declaration/definition of a
    templated function (as opposed to a header file + source file). But this gets tricky when
    nesting templated function calls and trying to instantiate them with new types.

!!! note "Extern Templates"
    While **extern template** might seem like a good idea, they will only save time on code
    generation, not parsing. If your templated function only need to support a finite number of
    fundamental types, moving their definition into a separate source file will save you the
    additional parsing overhead and avoid header pollution.

### Limit Header Pollution

Remember that a large portion of a compiler's time is spent parsing headers. STL headers in
particular will have various impact on compilation times. Some headers like `<type_traits>` will
have a minimal overhead, while `<filesystem>` or `<regex>` can take more than 200ms to parse on a
powerful machine. See [this website](https://artificial-mind.net/projects/compile-health/) for
detailed statistics on all STL headers.

To limit compilation overhead due to header parsing, you can do the following:

- [Profile](compilation-profiling.md) your compilation times to find out which header takes the most
  time to parse.
- Separate your code between source and header files. Move header includes to the .cpp if they are
  not needed in the .h.
- Separate expensive headers from cheap-but-commonly-used ones, and only include what you need.
- **Avoid** having a `all.h` or `common.h` that include all headers from your library. This may seem
  convenient, but will increase compilation times for your users.
- Use forward declarations to avoid pulling expensive headers.
- Use the [PIMPL idiom](#the-pimpl-idiom) to hide implementation details from header files of a
  class.

!!! tip "Forward Declarations And Pass-By-Value"
    I was surprised to learn that you can declare a function taking a forward declared class as a
    by-value argument and as a result. I.e. this works just fine:

    ```c++
    class type;
    type function(type);
    ```

!!! warning "Forward Declarations And Circular Dependencies"
    The Google C++ Style Guide cautions [against using forward
    declarations](https://google.github.io/styleguide/cppguide.html#Forward_Declarations) whenever
    possible. Forward declaration can hide circular dependencies which should be a red flag in your
    code architecture. My advice would be to use them sparingly when it makes sense, and measure the
    performance impact on your project when possible.

### The PIMPL idiom

!!! tip "TL;DR"
    Use [valuable::value_ptr<>](https://github.com/LoopPerfect/valuable) or
    [spimpl::impl_ptr<>](https://github.com/oliora/samples).

When defining a class in C++, the types of its member variables need to be known, as the compiler
needs to determine the size of the object. However, sometimes we have private member variables whose
type do not need to be exposed in the class header. Their type is an implementation detail, and we
do not want to expose the additional dependency.

The PIMPL idiom (Pointer to IMPLementation) is a technique to hide this implementation detail, such
that the underlying types used in a class are not exposed in the class header. Of course there is a
small price to pay. In most cases this means an extra heap allocation and pointer indirection.
Oftentimes the trade-off is worth it, but this depends on your specific use case.

There are several ways to implement a PIMPL in your code (from bad to good):

1. **[Bad]** Use a raw `T * m_foo;` member variable and forward-declare `T`. But this is **bad**
   because there is no lifetime management (when the encapsulating class is destroyed/moved/copied,
   etc.).
    ```c++
    class HiddenType;

    class Bar {
    protected:
        // No lifetime management = bad
        HiddenType * m_foo;
    };
    ```
2. **[Not Great]** Use a `std::unique_ptr<T> m_foo`. This would work, but there are two problems
   with that.
    1. The `std::unique_ptr<>` needs to know how to destroy the object, so you need to define the
       encapsulating class destructor _in the .cpp_ source file, or you would be forced to pull
       `<HiddenType.h>` in `<Bar.h>`.

        === "Bar.h"
            ```c++
            class HiddenType;

            class Bar {
                ~Bar();
            protected:
                std::unique_ptr<HiddenType> m_foo;
            };
            ```

        === "Bar.cpp"
            ```c++
            #include <HiddenType.h>

            // The destructor needs to know HiddenType
            Bar::~Bar() = default;
            ```

    2. You lose value semantics on the encapsulating type. I.e. you can no longer copy the object
       easily, just move it.

3. **[Not Great]** Use a `std::shared_ptr<T> m_foo`. This has the same issues as the
   `std::unique_ptr<>` solution. You lose value semantics, but you may also incur additional bugs
   due to the shared ownership of the hidden object (e.g. in case a copy of `Bar` is created).
4. **[Good]** Use a thin-wrapper around `std::unique_ptr<>` that provides copy/value semantics. Here
   are some readily available single-file implementations:
    - [valuable::value_ptr<>](https://github.com/LoopPerfect/valuable) (with accompanying [blog
      post](https://hackernoon.com/value-ptr-the-missing-c-smart-pointer-1f515664153e)).
    - [spimpl::impl_ptr<>](https://github.com/oliora/samples) very similar.

!!! warning "Pointers & Const-Correctness"
    When storing member variables that are pointers to data, you need to be very careful regarding
    **const-correctness**.
    ```c++
    #include <ExplicitType.h>

    class Bar {
        ~Bar();
    public:
        // Will compile, but this is NOT ok
        ExplicitType & get_foo_bad() const { return *m_foo; }

        // Const accessors should return pointers/reference to _const_ data.
        const ExplicitType & get_foo_good() const { return *m_foo; }

        // This is a const method, so it should return a pointer to a _const_ data.
        std::shared_ptr<const ExplicitType> get_foo_ptr() const { return m_foo; }

    protected:
        std::shared_ptr<ExplicitType> m_foo;
    };
    ```

!!! example
    An example usage of the PIMPL idiom in Lagrange is the `AttributeManager` class in
    [SurfaceMesh.h]({{ repo_url }}/blob/main/modules/src/SurfaceMesh.cpp).

### X Macro Trick For Explicit Instantiations

Repeating explicit template instantiations for various types can be a tedious task. It makes code
lengthy, hard to read and hard to extend when adding new types/functions to your codebase.
Fortunately we can use a cool preprocessor trick known as [X
macros](https://en.wikipedia.org/wiki/X_Macro) to iterate over a list of types and generate a list
of explicit template instantiation for various classes/functions.

While you could use the Boost Preprocessing library and macros such as `BOOST_PP_SEQ_FOR_EACH`, you
can also roll out your own solution, which requires very little code and is easy to understand.

The basic idea is as follows:

=== "Attribute.h"

    ```c++
    #pragma once

    #include <vector>
    ​
    namespace mylib {

    template<typename T>
    struct Attribute {
        void some_method();
        std::vector<T> m_data;
    };

    } // namespace mylib
    ```

=== "AttributeTypes.h"

    ```c++
    #pragma once

    // Define the X macro arguments here (= the list of types to instantiate)
    #define MYLIB_ATTRIBUTE_X(mode, data) \
        MYLIB_X_##mode(data, int8_t) \
        MYLIB_X_##mode(data, int16_t) \
        MYLIB_X_##mode(data, int32_t) \
        MYLIB_X_##mode(data, int64_t) \
        MYLIB_X_##mode(data, uint8_t) \
        MYLIB_X_##mode(data, uint16_t) \
        MYLIB_X_##mode(data, uint32_t) \
        MYLIB_X_##mode(data, uint64_t) \
        MYLIB_X_##mode(data, float) \
        MYLIB_X_##mode(data, double)
    ```

=== "Attribute.cpp"

    ```c++
    #include <mylib/Attribute.h>

    namespace mylib {

    template <typename T>
    void Attribute<T>::some_method() {
        // do something
    }

    // Explicit template instantiation using X macros
    #include <mylib/AttributeTypes.h>
    #define MYLIB_X_attr_class(_, T) template class Attribute<T>;
    MYLIB_ATTRIBUTE_X(attr_class, 0)
    #undef MYLIB_X_attr_class

    } // namespace mylib
    ```

!!! note "Macro Cleanup"
    There is no need to `#undef MYLIB_X_attr_class` at the end of `Attribute.cpp`, since the macro
    is usually defined at the _end_ of a .cpp file. But if you are planning on doing [Unity
    builds](https://cmake.org/cmake/help/latest/prop_tgt/UNITY_BUILD.html) and are _not_ using
    unique names for your macro, then it is a good idea to do so.

The above solution works well for a single list of types to instantiate. But what if we are mixing
functions that depend on two different types `U` and `T`? This is where the extra parameter `data`
comes in. You can think of it as a continuation parameter to recursively instantiate nested type
lists.

Here is an concrete example:

=== "Header.h"

    ```c++
    #pragma once

    #include <vector>

    template<typename T>
    struct Attribute {
        void some_method();
        std::vector<T> m_data;
    };

    template<typename Scalar>
    struct Mesh {
        std::vector<Scalar> m_vertices;
    };

    template<size_t Dim>
    struct Volume {
        size_t m_volume = Dim;
    };

    template<typename T, typename Scalar>
    void set_attribute(Mesh<Scalar> &mesh, const Attribute<T> &attr);

    template<typename T, typename Scalar, size_t D>
    void set_volume(Mesh<Scalar> &mesh, const Attribute<T> &attr, Volume<D> &vol);
    ```

=== "Types.h"

    ```c++
    #pragma once

    // Define the X macro arguments for each type list

    #define MYLIB_ATTRIBUTE_X(mode, data) \
        MYLIB_X_##mode(data, int8_t) \
        MYLIB_X_##mode(data, int16_t) \
        MYLIB_X_##mode(data, int32_t) \
        MYLIB_X_##mode(data, int64_t) \
        MYLIB_X_##mode(data, uint8_t) \
        MYLIB_X_##mode(data, uint16_t) \
        MYLIB_X_##mode(data, uint32_t) \
        MYLIB_X_##mode(data, uint64_t) \
        MYLIB_X_##mode(data, float) \
        MYLIB_X_##mode(data, double)

    #define MYLIB_MESH_X(mode, data) \
        MYLIB_X_##mode(data, double) \
        MYLIB_X_##mode(data, float)

    #define MYLIB_VOL_X(mode, data) \
        MYLIB_X_##mode(data, 2) \
        MYLIB_X_##mode(data, 3)
    ```

=== "Source.cpp"

    ```c++
    #include "Header.h"
    #include "Types.h"

    // Method/function definitions in the source file

    template <typename T>
    void Attribute<T>::some_method() {
        // do something
    }
    ​
    template<typename T, typename Scalar>
    void set_attribute(Mesh<Scalar> &mesh, const Attribute<T> &attr) {
        // do something
    }
    ​
    template<typename T, typename Scalar, size_t D>
    void set_volume(Mesh<Scalar> &mesh, const Attribute<T> &attr, Volume<D> &vol) {
        // do something
    }

    // Explicit instantiation
    ​
    // 1. Simple type lists (Attribute<> and Mesh<> classes)
    #define MYLIB_X_attr_class(_, T) template class Attribute<T>;
    MYLIB_ATTRIBUTE_X(attr_class, 0)
    ​
    #define MYLIB_X_mesh_class(_, S) template class Mesh<S>;
    MYLIB_MESH_X(mesh_class, 0)
    ​
    // 2. Cartesian product with two types S x T
    #define MYLIB_X_attr_set(S, T) template void set_attribute(Mesh<S> &mesh, const Attribute<T> &attr);
    #define MYLIB_X_mesh_set(_, S) MYLIB_ATTRIBUTE_X(attr_set, S)
    ​
    MYLIB_MESH_X(mesh_set, 0)
    ​
    // 3. Cartesian product with three types S x D x T.
    //    We need to define helper macros to unpack argument tuples.
    #define fst(first, second) first
    #define snd(first, second) second
    #define MYLIB_X_attr_vol(SD, T) template void set_volume(Mesh<fst SD> &mesh, const Attribute<T> &attr, Volume<snd SD> &vol);
    #define MYLIB_X_mesh_vol(D, S) MYLIB_ATTRIBUTE_X(attr_vol, (S, D))
    #define MYLIB_X_dim_vol(_, D) MYLIB_MESH_X(mesh_vol, D)
    ​
    MYLIB_VOL_X(dim_vol, 0)
    ```
