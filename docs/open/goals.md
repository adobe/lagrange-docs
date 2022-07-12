# Library Goals & Design Principles

There are a lot of geometry processing libraries out there, and it might be a little confusing where
Lagrange stands in the current landscape. In this page, we highlight some of the goals and key
design principles that go into Lagrange.

1. **Do Not Reinvent The Wheel**. If a library exists that already solves a particular problem
   (nanoflann, embree, etc.) we will use it instead of reinventing the wheel. As such, we have
   libigl-style wrappers around some common third-party libraries. Note that we only use external
   libraries that are available under *commercial friendly* licenses. Please consult our [dedicated
   page](third-party.md) for more information.

2. **Powerful Mesh Data Structure**. Our mesh data structure can represent any type of mesh
   (triangle mesh, quad-dominant, polygonal mesh, 2D, 3D, etc.). It is memory-efficient, support
   generic attributes, navigation, dynamic editing, etc. More information is available on our
   dedicated [Mesh Class](user/core/mesh.md) user guide.

3. **Interoperability**. Our mesh data structure is designed to allow wrapping any continuous
   buffers as regular mesh attributes. This allows creating a Lagrange mesh from an external buffer
   without copying any data, as long as memory layout is compatible. Furthermore, you can export
   attributes to reuse our buffers after a mesh object is destroyed. And because our attributes can
   be viewed as Eigen matrices, our mesh data structure is directly compatible with libigl. We are
   planning to implement conversion functions for other mesh processing libraries in the future.

    ??? info "Interoperability With Others Libraries"
        | Name | From Lagrange Mesh | To Lagrange Mesh | Comment |
        |------|--------------------|------------------|---------|
        | [cinolib](https://github.com/mlivesu/cinolib)                         | :x: | :x: | |
        | [geogram](http://alice.loria.fr/software/geogram/doc/html/index.html) | :x: | :x: | Planned. |
        | [geometry-central](http://geometry-central.net/)                      | :x: | :x: | Planned. |
        | [libigl](https://libigl.github.io/)                                   | :heavy_check_mark: (no copy) | :heavy_check_mark: (may copy) | |
        | [pmp-library](http://www.pmp-library.org/)                            | :x: | :x: | |

4. **Clean Build System**. Lagrange has a clean and polished CMake build system. Getting started
   with Lagrange is incredibly simple, just add 5 lines to your CMake project (no git submodule
   needed):

    ```cmake
    include(FetchContent)
    FetchContent_Declare(lagrange
        GIT_REPOSITORY <lagrange-url>
        GIT_TAG        <sha256>
    )
    FetchContent_MakeAvailable(lagrange)

    target_link_libraries(my_project PUBLIC lagrange::core)
    ```

    If you are not a fan of CMake, all Lagrange modules follow the same organization, so it should
    be easy to add them to your build system, provided you can compile the required dependencies.

5. **Ease Of Use**. Lagrange meshes have a clean and well-documented API. Any mesh attribute can be
   viewed as a Eigen matrix, ensuring compatibility with libigl functions. Combined with our simple
   CMake system, Lagrange is an ideal framework for prototyping C++ applications with advanced
   geometry processing features.

6. **Modularity**. Lagrange features are split into modules, based on specific features and
   dependencies. Module names are sensible and short. While `lagrange::core` is relatively small,
   bringing additional modules to your project can provide more advanced features.

7. **File Formats**. Our IO module supports reading/writing a variety of standard file formats used
   in the industry. Rather than writing our own parsers, we leverage existing libraries such as
   tinyobj to provide IO functionalities.

    ??? info "Supported File Formats"
        | Format | Read | Write | Comment            |
        |--------|------|-------|--------------------|
        | OBJ    | :heavy_check_mark: | :heavy_check_mark: | Via tinyobj/libigl |
        | VTK    | :x:                | :heavy_check_mark: | Custom writer      |
        | PLY    | :heavy_check_mark: | :heavy_check_mark: | Via tinyply/libigl |
        | OFF    | :heavy_check_mark: | :heavy_check_mark: | Via libigl         |
        | glTF   | :heavy_check_mark: | :x:                | Via Assimp         |
        | FBX    | :heavy_check_mark: | :x:                | Via Assimp         |
        | USD    | :x:                | :x:                | Planned            |
        | HDF5   | :x:                | :x:                | Planned            |

8. **Performance**. Lagrange functions are written with performance in mind. We use TBB for
   multithreading, and avoid unnecessary heap memory allocation or data copies. Lagrange should be
   able to process large assets that are often encountered in the industry. If you encounter any
   performance limitation, please reach out to us.

9. **Advanced Viewer**. We provide an advanced mesh viewer for building interactive applications with realistic shading. We use a modified ImGui that conforms to the [Spectrum](https://spectrum.adobe.com/) specification to provide a user experience more consistent with Adobe products.

    ??? info "Viewer Key Features"
        - Support for all lagrange mesh types
        - Customizable renderer that includes PBR
        - Gizmos for interactive mesh and element manipulation
        - Easy to add your own UI via ImGui
        - Variety of visualization options - mix and match indexing/colormapping/rendered primitive/shading.


10. **Robustness/Support**. Being backed by a company, Lagrange has a strong focus on correctness/being as bug free as possible. We have extensive unit testing internally, with more than 400 unit tests. Specifically, we try to ensure the following:
    - **Corner Cases**. Special cases should not crash the program. Incorrect inputs may result in exceptions being thrown.
    - **Determinism**. Parallel algorithms should produce the same results when called repeatedly with the same inputs.
    - **Regression Tests**. We should have unit tests to ensure that algorithms produce the same output whenever code changes. Changes in algorithm behaviors should be documented.
    - **Cross-Platform**. Algorithms should produce the same result on all three platforms whenever possible (macOS/Linux/Windows). This means avoiding `std::default_random_engine` and other platform-specific constructs.
11. **Useful Feedbacks**. Being integrated into a product means we often need to provide some simple feedback mechanisms, such as logging, cancellation and progress report.
    - **Logger**. We use [spdlog](https://github.com/gabime/spdlog) to provide beautiful logging messages. The global logger is thread-safe, and can be turned off or redirected as needed by the client application.
    - **Cancellation**. It should be possible to cancel any running function by switching a `std::atomic_bool &` flag.
    - **Progress Report**. A simple thread-safe callback mechanism can be used in certain functions to report progress. This is useful to inform the user about the advancement of certain tasks that can be slow (e.g. mesh cleanup, etc.).
    - **Error Mechanism**. We use exception throwing as the mechanism to report an error. While returning error code has certain advantages over exceptions, third-party libraries or the STL can still throw exceptions, and thus it is the user's responsibility to catch them should they occur.
12. **Documentation/Code Style**. Our codebase is formatted via clang-format for consistency. We aim to provide both libigl-style tutorials to get started using Lagrange, as well as detailed API documentation written in Doxygen.
