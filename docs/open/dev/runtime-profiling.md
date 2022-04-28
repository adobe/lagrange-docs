# Runtime Profiling with Tracy

[Tracy](https://github.com/wolfpld/tracy) is a real-time profiler using a client/server model. It is
cross-platform (Windows, Linux, macOS) and support GPU (OpenGL, Vulkan, etc.). This page explains
how to use Tracy with Lagrange.

{% if is_corp %}
![](../../corp/dev/img/tracy.png)
{% else %}
![](https://raw.githubusercontent.com/wolfpld/tracy/master/doc/profiler.png)
{% endif %}

## Enabling The Tracy Client

Tracy uses a client-server model to profile applications. This means we need to inject the Tracy
client (a single .cpp file) into our application to enable profiling. To enable the Tracy client
with Lagrange, simply enable the CMake option `LAGRANGE_WITH_TRACY` in your CMake setup.

!!! info "Compile Options"
    On macOs and Linux, do not forget to compile your application with `-g`,
    `-fno-omit-frame-pointer`, and `-rdynamic` (see tracy manual for explanations). When using
    `LAGRANGE_WITH_TRACY=ON`, those options will be automatically enabled by the Lagrange CMake.

## Instrumenting Your Code

The next step will be to instrument your code. In short:

1. Include `<Tracy.hpp>` in every file you are interested in profiling.
2. Add the macro `FrameMark` at the end of each frame loop.
3. Add the macro `ZoneScoped` as the first line of your function definitions to include them in the
   profile.

!!! tip "Convenience Macros"
    Since Tracy is an optional dependency in Lagrange, we provide a convenience header to include
    Tracy without having to test the `TRACY_ENABLE` macro:

    ```c++
    #include <lagrange/utils/tracy.h>
    ```

    This header provides the following alias macros for Tracy:

    - `LAGRANGE_ZONE_SCOPED` for `ZoneScoped`
    - `LAGRANGE_FRAME_MARK` for `FrameMark`

    When Tracy is disabled (`LAGRANGE_WITH_TRACY=OFF` in CMake), these macros will expand to a no-op.

## Running The Tracy Profiler

Make sure to compile the profiler (server) using the same version of Tracy as in Lagrange. The
easiest way to do so is to build from the `<build>/_deps/tracy-src`. This folder is downloaded by
CMake when building Lagrange with `LAGRANGE_WITH_TRACY=ON`.

### Windows

1. Download the pre-built binaries corresponding to the version of Tracy used in Lagrange (see
   `cmake/recipes/external/tracy.cmake`).
2. Run the Tracy executable and your program.
3. Click "Connect" in the Tracy profiler.

### macOS

1. Install prerequisites using homebrew
    ```
    brew install freetype capstone gtk glfw
    ```
2. Build the profiler (server):
    ```
    cd <build>/_deps/tracy-src/profiler/build/unix
    make release -j8
    ```
3. Run the profiler:
    ```
    ./Tracy-release
    ```
4. Run your program, and click "Connect" in the Tracy profiler.
