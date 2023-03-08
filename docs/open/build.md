# Compilation Instructions

## Build

Lagrange requires a modern C++ compiler that supports C++17 features.
Lagrange data structures are compatible with [Eigen](https://eigen.tuxfamily.org/) matrices.
Other dependencies such as
[libigl](https://github.com/libigl/libigl) and
[imgui](https://github.com/ocornut/imgui) will be downloaded by the build system as needed.

### Checkout

To checkout the code:

```sh
git clone {{ repo_git }}
```

### Compiling

To build the code:

```sh
cd Lagrange
mkdir build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
```

You can then select the Lagrange modules to build with `cmake-gui .` or specify them from command line with:

```sh
cmake .. -DLAGRANGE_MODULE_<name>=ON # For example, -DLAGRANGE_MODULE_UI=ON
```

To see available CMake options, please take a look at the file [{{ cmake_option_file }}]({{ repo_url
}}/blob/main/{{ cmake_option_file }}) in the root of the Lagrange repository.

{% if is_corp %}

!!! tip "Network Connection"
    Since CMake will download third-party dependencies via
    [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html), you need to be on
    the Adobe VPN when running the initial CMake configuration & download of unit test data.

{% endif %}

!!! tip "Setting Up CMake Options"
    Lagrange has a lot of CMake options that can be configured. It may not be practical to pass
    those options via command-line, and manually checking boxes in CMake-GUI can be tedious. To
    facilitate setting up CMake options for Lagrange, simply rename `{{ cmake_option_file }} ->
    LagrangeOptions.cmake` and uncomment options that you wish to change.

    Note that since options are cached by CMake, you will need to delete your
    `<build>/CMakeCache.txt` before re-running CMake in order for a change in
    `LagrangeOptions.cmake` to take effect.

!!! tip "Useful CMake Options"

    * `LAGRANGE_UNIT_TESTS`: build unit tests.
    * `LAGRANGE_PERFORMANCE_TESTS`: build performance tests.
    * `LAGRANGE_EXAMPLES`: build examples.
    * `LAGRANGE_USE_PCH`: build with precomplied headers.
    * `LAGRANGE_WITH_ONETBB`: build with oneTBB.
    * `LAGRANGE_WITH_TRACY`: build with tracy profiling support.
    * `USE_SANITIZER`: build with sanitizer support, options are "Address", "Memory", "MemoryWithOrigins", "Undefined", "Thread", "Leak".

Finally, build with

```sh
cmake --build .
```

!!! question "Compilation Issues"
    If an issue occurs during compilation, especially after an update, try to

    1. Delete your `<build>/CMakeCache.txt` and re-run CMake to configure your project.
    2. The nuclear option: delete the whole `<build>` folder and re-run CMake to configure your project.

    If neither option works, please ask for help on [#lib-lagrange](https://adoberesearch.slack.com/archives/CLNGBC44V).

### Unit Tests

{% if is_corp %}

!!! warning "Artifactory Access"
    Building unit tests requires Artifactory to be setup. Please read our [Getting
    Started](setup.md) page for instructions on how to configure your API key.

{% endif %}

When `LAGRANGE_UNIT_TESTS` is `ON`, unit tests are built automatically. To run all unit tests,
either run the special target `RUN_TESTS` in your Visual Studio/Xcode project, or simply run `ctest`
in the command-line in your build folder. Further instructions on running unit tests are available
on [this page](dev/unit-tests.md).


## Platform-Specific Steps

### Windows

For Visual Studio, you might have to force 64-bit compilation depending on your exact compiler
version, e.g.:

```sh
cmake -A x64 ..
cmake -G "Visual Studio 17 2022" -A x64 ..
cmake -G "Visual Studio 16 2019" -A x64 ..
cmake -G "Visual Studio 15 2017 Win64" ..
cmake -G "Visual Studio 14 2015 Win64" ..
```

### Unix

You may have to install Zenity for the file dialog window to work:

```sh
sudo apt-get install zenity
```

## Run

Executables are compiled into the following folders:

- `<build>/examples` for examples covering various Lagrange features.
- `<build>/tests` for unit test executables.
- `<build>/performance` for performance test executables (legacy code).

## Dependencies

Lagrange's CMake build system will download and build any and all dependencies required by the
current build setup. This includes both core dependencies (e.g., Eigen) and optional ones (e.g.,
tinyobjloader for the IO module). If you are using Lagrange in your project and you wish to override
Lagrange dependencies, make sure they are specified as CMake targets before calling
`add_subdirectory(<lagrange>)`.
