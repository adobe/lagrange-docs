{% if is_corp %}
{% include 'corp/third-party.md' %}
{% else %}
## External Dependencies

Here is a list of third party libraries used in Lagrange. Those external dependencies will be
automatically downloaded by our CMake system depending on which Lagrange module is enabled.

!!! important
    This table only lists **direct** dependencies of various Lagrange modules. Indirect dependencies
    are not listed there. {% if is_corp %} For example, OpenVDB depends on Boost, TBB and IlmBase.
    Anorigami depends on Armadillo, SuperLU, Vc, etc. {% endif %}

| Library Name                                                                 | License               | Used By                                       |
|------------------------------------------------------------------------------|-----------------------|-----------------------------------------------|
| [Assimp](https://github.com/assimp/assimp)[^0_assimp]                        | BSD-3                 | IO                                            |
| [Boost](https://www.boost.org/)[^1_boost]                                    | Boost                 | FS                                            |
| [CLI11](https://github.com/CLIUtils/CLI11)                                   | BSD-3                 | Examples (Core, UI), Performance Tests (Core) |
| [Catch2](https://github.com/catchorg/Catch2)                                 | Boost                 | Testing                                       |
| [Dear ImGui](https://github.com/ocornut/imgui)                               | MIT                   | UI                                            |
| [Eigen](https://eigen.tuxfamily.org/)                                        | MPL2                  | Core, UI                                      |
| [EnTT](https://github.com/skypjack/entt)                                     | MIT                   | UI                                            |
| [Filesystem](https://github.com/gulrak/filesystem)[^2_filesystem]            | MIT                   | FS                                            |
| [GLFW](https://github.com/glfw/glfw)                                         | MIT                   | UI                                            |
| [ImGuizmo](https://github.com/CedricGuillemet/ImGuizmo)                      | MIT                   | UI                                            |
| [JSON for Modern C++](https://github.com/nlohmann/json)                      | MIT                   | UI                                            |
| [Libigl](https://github.com/libigl/libigl/)                                  | MPL2                  | Core, IO                                      |
| [MDL SDK](https://developer.nvidia.com/mdl-sdk)                              | BSD-3                 | UI                                            |
| [MshIO](https://github.com/qnzhou/MshIO)                                     | Apache 2              | IO                                            |
| [Portable File Dialogs](https://github.com/samhocevar/portable-file-dialogs) | WTFPL (public domain) | UI                                            |
| [Pybind11](https://github.com/pybind/pybind11)                               | BSD-3                 | Python                                        |
| [Threading Building Blocks](https://github.com/oneapi-src/oneTBB)            | Apache 2              | Core                                          |
| [Tracy](https://github.com/wolfpld/tracy)[^3_tracy]                          | BSD-3                 | Core                                          |
| [gl3w](https://github.com/skaslev/gl3w)                                      | MIT                   | UI                                            |
| [imgui fonts](https://github.com/HasKha/imgui-fonts)                         | MIT                   | UI                                            |
| [nanoflann](https://github.com/jlblancoc/nanoflann)                          | BSD-2                 | UI                                            |
| [span-lite](https://github.com/martinmoene/span-lite)                        | Boost                 | Core                                          |
| [spdlog](https://github.com/gabime/spdlog)                                   | MIT                   | Core                                          |
| [stb](https://github.com/nothings/stb)                                       | Public domain         | UI                                            |
| [tinyobjloader](https://github.com/tinyobjloader/tinyobjloader)              | MIT                   | IO                                            |

[^0_assimp]:      Assimp is an optional dependency of the IO module.
[^1_boost]:       Boost::filesystem is an optional backend of the FS module.
[^2_filesystem]:  `gulrak/filesystem` is only needed when the IO module is compiled in C++14 mode. In C++17 mode, the IO module will defaults to `std::filesystem`.
[^3_tracy]:       Tracy is an optional dependency of the core module.

## Bundled Dependencies

Lagrange integrates some third-party code directly into its codebase. Those files have usually been
modified to work with Eigen, and their functions wrapped into the `lagrange` namespace. This table
summarize the list of third-party code that is directly bundled into Lagrange, as well as the
appropriate licenses and files that are affected.

| Library Name                                                                                                                   | License       | Used By            | Files                                                                                                                                                                                                                                                      |
|--------------------------------------------------------------------------------------------------------------------------------|---------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [CMake Scripts](https://github.com/StableCoder/cmake-scripts)                                                                  | Apache 2      | CMake Build System | [sanitizers.cmake]({{ repo_url }}/blob/main/cmake/recipes/external/sanitizers.cmake), [code-coverage.cmake]({{ repo_url }}/blob/main/cmake/recipes/external/code-coverage.cmake)                                                                           |
| [Earcut](https://github.com/mapbox/earcut.hpp)                                                                                 | ISC           | Core               | [earcut.h]({{ repo_url }}/blob/main/modules/core/src/mapbox/earcut.h)                                                                                                                                                                                      |
| [Floating-point exception handling example](http://www-personal.umich.edu/~williams/archive/computation/fe-handling-example.c) | Public domain | Core               | [fpe.cpp]({{ repo_url }}/blob/main/modules/core/src/fpe.cpp)                                                                                                                                                                                               |
| [function_ref](https://github.com/TartanLlama/function_ref)                                                                    | CC0           | Core               | [function_ref.h]({{ repo_url }}/blob/main/modules/core/include/lagrange/utils/function_ref.h)                                                                                                                                                              |
| [Geogram](https://github.com/BrunoLevy/geogram)                                                                                | BSD-3         | Core               | [point_triangle_squared_distance.h]({{ repo_url }}/blob/main/modules/core/include/lagrange/point_triangle_squared_distance.h), [point_segment_squared_distance.h]({{ repo_url }}/blob/main/modules/core/include/lagrange/point_segment_squared_distance.h) |
| [ImGui Progress Indicators](https://github.com/ocornut/imgui/issues/1901)                                                      | MIT           | UI                 | [progress.h]({{ repo_url }}/blob/main/modules/ui/include/lagrange/ui/imgui/progress.h), [progress.cpp]({{ repo_url }}/blob/main/modules/ui/src/imgui/progress.cpp)                                                                                         |
| [scope_guard](https://github.com/ricab/scope_guard/blob/master/scope_guard.hpp)                                                | Public domain | Core               | [scope_guard.h]({{ repo_url }}/blob/main/modules/core/include/lagrange/utils/scope_guard.h)                                                                                                                                                                |
| [Shewchuk's predicates](https://www.cs.cmu.edu/~quake/robust.html)                                                             | Public domain | Core               | [predicates.cpp]({{ repo_url }}/blob/main/modules/core/src/predicates.cpp)                                                                                                                                                                                 |
| [valuable](https://github.com/LoopPerfect/valuable)                                                                            | MIT           | Core               | [value_ptr.h]({{ repo_url }}/blob/main/modules/core/include/lagrange/utils/value_ptr.h)                                                                                                                                                                    |

{% endif %}
