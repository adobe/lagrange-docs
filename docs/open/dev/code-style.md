# Code Style

!!! tip "Apply Clang Format"
    Our code style configuration is stored in a file `.clang-format` at the root of the repository.
    It is highly recommended that you install and configure
    [ClangFormat](https://clang.llvm.org/docs/ClangFormat.html) for your favorite editor. This will
    allow you to automatically format your code to adopt a consistent style with the rest of
    Lagrange.

We follow the [Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html), modified
for the needs of the Lagrange project. To get a quick taste of our style, here is a simple function
declaration:

```C++
#include <lagrange/compute_vertex_normal.h>

namespace lagrange {

/**
 * One sentence description of the function.
 *
 * More detailed description (optional).
 *
 * @param[in]  input_mesh  Input mesh description.
 *
 * @tparam     MeshType    Mesh type.
 */
template <typename MeshType>
void process_mesh(std::shared_ptr<MeshType> input_mesh)
{
    ...
    compute_vertex_normal(input_mesh);
    ...
}

} // namespace lagrange
```

and here is an example for class declaration:

```C++
namespace lagrange {

/**
 * One sentence description of the class.
 *
 * @tparam     MeshType  Mesh type.
 */
template <typename MeshType>
class MeshProcesser
{
public:
    /**
     * One sentence description.
     *
     * @param[in]  mesh  Mesh description.
     */
    void set_mesh(std::shared_ptr<MeshType> mesh)
    {
        // Inline comment
        m_mesh = mesh;
    }

private:
    std::shared_ptr<MeshType> m_mesh;
};

} // namespace lagrange
```


Here are a few items to highlight:

- Indentation consists of __4 spaces__.
- Keep each line below 100 characters long.
- All functions and classes should be inside of the `lagrange` namespace.
    - All the code in the `core` module lives directly under the `lagrange` namespace.
    - Individual modules use their own sub-namespace, e.g. `lagrange::io`.
- C++ `namespace` is not indented.
- Function and variable names are in [__snake_case__](https://en.wikipedia.org/wiki/Snake_case) while class names are in [__CamelCase__](https://en.wikipedia.org/wiki/Camel_case).
- Member variables are prefixed with `m_`.
- The opening bracket placement is dictated by our `.clang-format`: always attach braces to surrounding context, except for functions and classes, where it is placed on a newline.
- Commented/dead code should be removed.
- New code is encouraged to use Doxygen-style comments if possible, in particular for public headers. Here is an example for a [function]({{ repo_url }}/blob/main/modules/core/include/lagrange/utils/strings.h), and for a [class]({{ repo_url }}/blob/main/modules/core/include/lagrange/SurfaceMesh.h).
- When in doubt, we recommend using fenced `/** */` blocks for function/class descriptions, and `//` for inline comments.
- `#include` statement uses full path in angle brackets, for example:
  ```cpp
  #include <lagrange/filename.h>
  ```
- The order of `#include` statements should be local to global, as explained in [this post](https://stackoverflow.com/a/2762596):
    1. Immediate `.h` file that this file is implementing if applicable.
    2. Lagrange headers.
    3. Third party dependency headers if any.
    4. C/C++ system headers if any.

Lastly, no style guide is complete or correct all the time. Older code in Lagrange may not follow all the items described here. Use your professional judgment when necessary.
