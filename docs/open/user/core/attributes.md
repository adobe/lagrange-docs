# Mesh Attributes

!!! attention
    Since v6.0.0, Lagrange introduced a new polygonal mesh class that is meant to replace the
    original mesh class used throughout Lagrange. While currently few of the Lagrange functions use
    this new mesh class, over time old and new features will transition to use this new data
    structure.

<!-- @header
#include <lagrange/SurfaceMesh.h>
#include <lagrange/Attribute.h>
#include <lagrange/views.h>
#include <lagrange/foreach_attribute.h>
#include <lagrange/Logger.h>
#include <vector>
#include <random>
using Scalar = double;
using Index = uint64_t;
-->

Mesh attributes are buffers of data associated to a mesh element. They are characterized by the following:

- **Name**: A string that uniquely identifies the attribute in the mesh, irrespectively of which
  mesh element it is associated to.
- **Id**: A 32bit unsigned integer that uniquely identifies the attribute in the mesh. Ids are
  assigned at attribute creation and will not be invalidated if other attributes are
  removed/created.
- **Value Type**: Value type of the data being stored in the attribute. We only support fixed-sized
  integer and floating point types.

    ??? note "Supported Value Types (Click to expand)"
        - `int8_t`
        - `int16_t`
        - `int32_t`
        - `int64_t`
        - `uint8_t`
        - `uint16_t`
        - `uint32_t`
        - `uint64_t`
        - `float`
        - `double`

- **Element**: Type of mesh element the attribute is associated to. It can be one of the following:

    | `AttributeElement` | Description |
    |---|---|
    | `Vertex` | Attribute associated to mesh vertices (e.g., positions). |
    | `Facet` | Attribute associated to mesh facets. |
    | `Edge` | Attribute associated to mesh edges. |
    | `Corner` | Attribute associated to mesh facet corners (e.g. vertex indices). |
    | `Value` | Attribute that is **not** associated to any mesh element (arbitrary size). |
    | `Indexed` | A pair of (`Corner`, `Value`) attributes, where the corner attribute is an<br/>index into the value attribute buffer (e.g. a UV). |

    !!! note "Automatic Resizing"
        `Vertex`, `Facet`, `Edge` and `Corner` attributes are resized accordingly to their
        respective mesh element when inserting/removing vertices/facets, while a `Value` attribute
        is never resized automatically.

- **Usage**: A usage tag is an optional tag that can be used to determine how attribute values are
  affected by other mesh operations. See the [reference documentation][Attribute usage] for a list
  of available usage tags.

    !!! example
        When applying a rigid transform $M$ to a mesh, attributes with the `Normal` tag will be
        transformed according to $M^{-T}$. Similarly, when removing mesh vertices, attributes with
        the `VertexIndex` tag will be remapped accordingly.

- **Channels**: Number of channels for each mesh element in the attribute. The number of possible
  channels for an attribute is restricted by the attribute usage tag.

    !!! example
        An attribute with the `VertexIndex` tag must have a single channel, while attributes with
        the `Color` tag can have between 1 and 4 channels.

## Attribute Creation

To create a new attribute and return its id:

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// Minimal version only requires name + element type.
auto id0 = mesh.create_attribute<double>(
    "color",
    lagrange::AttributeElement::Corner);

// Optionally specify usage tag + num channels.
auto id1 = mesh.create_attribute<float>(
    "normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    3);

// View attribute as a Eigen::Map<const ...>
auto attr_matrix = matrix_view(mesh.get_attribute<float>(id1));
```

## Accessing Attribute Values

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Returns a const Attribute<T> &
auto& attr = mesh.get_attribute<Scalar>("normals");

// Alternative: use id to retrieve attr (avoids a hash map lookup)
auto attr_id = mesh.get_attribute_id("normals");
auto& attr2 = mesh.get_attribute<Scalar>(attr_id);

// Wrap as an Eigen matrix as usual
auto attr_matrix = matrix_view(attr);
```

!!! tip "Using Attribute Ids"
    Using the attribute id instead of its name avoids a `std::string -> uint32_t` lookup. Since
    attribute ids are guaranteed to not be invalidated, you may also store it in your application
    (e.g. UI menus, etc.).

!!! important "Disabled Implicit Copies"
    It is important to note that implicit copies of an `Attribute` object is forbidden. Since
    Attribute buffers have value semantics (like `std::vector<>`), storing the result of
    `mesh.get_attribute<>()` in a `auto attr` variable would lead to an implicit copy. For this
    reason, the following code will **not** compile and produce an error:

    ```c++
    // The following will NOT compile (Attribute copy is explicit)
    // auto attr3 = mesh.get_attribute<float>("normals");
    ```

    Copy-on-write handling of attribute buffers is done at the mesh level, i.e. when copying a
    `SurfaceMesh` object, or when calling methods such as `SurfaceMesh::duplicate_attribute()`.

## Iterating Over Mesh Attributes

In many situation, it is desirable to iterate over existing mesh attributes to extract some
information, or process existing attributes. We provide utility functions to iterate over existing
mesh attributes, with additional filtering based on element types.

Basic example:
```c++
#include <lagrange/foreach_attribute.h>
#include <lagrange/Logger.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Iterate over each attribute sequentially
seq_foreach_attribute_read(mesh, [](auto&& attr) {
    lagrange::logger().info("Attribute with {} channels", attr.get_num_channels());
});

// Same, but retrieves attribute names while iterating
seq_foreach_named_attribute_read(mesh, [&](std::string_view name, auto&& attr) {
    lagrange::logger().info("Attribute named '{}' with {} channels",
        name, attr.get_num_channels());
});
```

Iterator functions follow the same naming convention, with variations being as follows:

| Variation | Description |
|---|---|
| **seq** vs **par** | Iterate sequentially or in parallel over available mesh attributes. |
| **named** vs unnamed | Whether to pass attribute names to the callback function .|
| **read** vs **write** | Whether read-only or writable references to the attributes are required. |

See [reference documentation][Attribute iteration] for additional details.

### Inferring Value Type

Since we use generic lambda to iterate over attributes of different types, it is possible to deduce
the value type of the current attribute in the following manner:

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

seq_foreach_attribute_read(mesh, [](auto&& attr) {
    // Retrieve the attribute value type within the lambda
    using AttributeType = std::decay_t<decltype(attr)>;
    using ValueType = typename AttributeType::ValueType;
    lagrange::logger().info("Attribute value type size: {}", sizeof(ValueType));
});
```

### Filtering Element Types

Since indexed attributes have a different interface from non-indexed attributes, it is often
necessary to use two different code path when iterating over mesh attributes. Fortunately, it is
possible to do so concisely thanks to C++17's `if constexpr()`, like so:

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Use compile-time if to check for indexed attributes
seq_foreach_named_attribute_read(mesh, [](std::string_view name, auto&& attr) {
    using AttributeType = std::decay_t<decltype(attr)>;
    if constexpr (AttributeType::IsIndexed) {
        lagrange::logger().info(
            "Indexed attribute '{}' with {} values",
            name,
            attr.values().get_num_elements());
    } else {
        lagrange::logger().info(
            "Non-indexed attribute '{}' with {} elements",
            name,
            attr.get_num_elements());
    }
});
```

Alternatively, one can provide an optional template argument to the  `foreach` function to iterate
over a specific element type:

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Iterate over non-indexed attributes
lagrange::seq_foreach_named_attribute_read<~lagrange::AttributeElement::Indexed>(
    mesh,
    [&](std::string_view name, auto&& attr) {
        lagrange::logger().info(
            "Attribute named '{}' with {} elements",
            name,
            attr.get_num_elements());
    });

// Iterate over indexed attributes only
lagrange::seq_foreach_attribute_read<lagrange::AttributeElement::Indexed>(
    mesh,
    [](auto&& attr) {
        using AttributeType = std::decay_t<decltype(attr)>;
        using ValueType = typename AttributeType::ValueType;
        using Index = typename AttributeType::Index;
        lagrange::logger().info(
            "Indexed attribute using value type size {} and index size {}",
            sizeof(ValueType),
            sizeof(Index));
    });
```

!!! note "Argument-Dependent Lookup"
    With this variant, [ADL](https://en.wikipedia.org/wiki/Argument-dependent_name_lookup) no longer
    work, so you need to explicitly call `lagrange::seq_foreach_attribute_read(mesh, ...)` rather
    than `seq_foreach_attribute_read(mesh, ...)`.

Finally, it is possible to combine template argument filters via bitwise boolean operations:

```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Iterate over vertex, facet and corner attributes:
lagrange::seq_foreach_attribute_read<
    lagrange::AttributeElement::Vertex | lagrange::AttributeElement::Facet |
    lagrange::AttributeElement::Corner>(mesh, [&](auto&& attr) {
    lagrange::logger().info(
        "Non-indexed attribute with {} elements",
        attr.get_num_elements());
});
```

### A Note On Thread-Safety

The following operations are **safe** to do in parallel:

- Writing to two separate mesh attributes pointing to the same buffer (a deep copy will be created).

The following operations are **not safe** to do in parallel:

- Writing to an attribute while creating other mesh attributes.
- Adding elements to a mesh while writing to another attribute of the same mesh.

From a practical standpoint, copy-on-write attributes behave as if each mesh owns its own
`std::vector<>` for each attribute. Adding an element to a mesh would resize the corresponding mesh
attributes, making concurrent writes unsafe. Creating new mesh attributes will move existing mesh
attributes, making concurrent writes also unsafe.

Note that if two meshes are shallow copies of each other, it is perfectly safe to add elements to
each of them concurrently. The same goes for writing in parallel to mesh attributes that are
duplicates of each others: each attribute behaves as if it owns its own copy of the data.

!!! attention "Temporary Copy On Concurrent Writes"
    While concurrent writing to mesh attributes is a thread-safe operation, note that it may
    sometimes create an unnecessary temporary copy of the data. To avoid this, we would need to
    block every write operation with a mutex, which would involve an expensive [context
    switch](http://ithare.com/infographics-operation-costs-in-cpu-clock-cycles/). Instead, we simply
    rely on the atomic counter from the `shared_ptr<>` to decide whether to copy/acquire ownership
    of the data. While this is a thread-safe operation, it may create a temporary copy of the data.

## Wrapping External Buffers

A key feature of our attribute system is the possibility to easily wrap external buffer and treat
them as regular mesh attributes, avoiding any data copy. As long as the data layout is compatible,
you will be able to wrap a continuous buffer as a mesh attribute and pass it around.

<!-- @attr -->
```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;
mesh.add_vertices(10);

Index num_verts = mesh.get_num_vertices();
Index num_coords = mesh.get_dimension();

// Create a flat buffer to use as external attribute data
std::vector<Scalar> normals(num_verts * num_coords);

// Wrap external buffer as a read-write attribute
mesh.wrap_as_attribute<Scalar>(
    "normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    num_coords,
    normals);

// Retrieves a Eigen::Map<> view of the attribute
auto N = lagrange::attribute_matrix_ref<Scalar>(mesh, "normals");

// Check that all coordinates are finite (no inf/nan).
assert(N.allFinite());
```

Sometimes, it is necessary to wrap a pointer to a **const** buffer, to ensure the external buffer
will not be be written to:

<!-- @attr -->
```c++
// Wrap external buffer as a read-only attribute
const Scalar *const_normals = normals.data();
mesh.wrap_as_const_attribute<Scalar>(
    "const_normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    num_coords,
    {const_normals, normals.size()});

// Non-const methods on the normal attr will throw an error
mesh.ref_attribute<Scalar>("const_normals").ref_all(); // --> throws an exception
```

!!! note "Non-Const Access"
    The following code does **not** throw an exception:
    <!-- @attr -->
    ```c++
    auto &attr = mesh.ref_attribute<Scalar>("const_normals");
    ```
    This is because while `attr` is a writable reference to the attribute `"const_normals"`, the
    user could decide to update the attribute itself to wrap another non-const buffer (via
    `attr.wrap(...)`). Only methods which provide write access to the actual buffer data (such as
    `attr.ref_all()`) will throw an exception.

Alternatively, instead of implicitly converting to a `span<>`, you can explicitly pass a `span<>`
object and let the compiler deduce the `Scalar` type template argument:

<!-- @attr -->
```c++
// Pass a `span<>` object directly to let the compiler deduce
// the template value type
mesh.wrap_as_const_attribute(
    "normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    num_coords,
    lagrange::span<const Scalar>(normals));
```

!!! tip "Tracking Ownership And Moving Eigen Matrices"
    If you need to track the ownership of an external buffer being wrapped as a mesh attribute,
    please read our documentation about [SharedSpan](../general-utilities/#shared-span) objects. Any
    `wrap_*` method that accepts a regular `span<>` object should also work with a managed
    `SharedSpan` object.

    Using a [SharedSpan](../general-utilities/#shared-span) object to wrap an external object as
    attribute allows moving a Eigen::Matrix and other arbitrary objects into mesh attributes without
    any extra buffer copy, as long as the memory layout of the coordinates are compatible.

## Delete And Export Attributes

To delete an attribute, simply call the eponymous method:

<!-- @delete -->
```c++
lagrange::SurfaceMesh<Scalar, Index> mesh;

// ...

// Delete attribute
mesh.delete_attribute("normals");
```

More interestingly, the attribute itself can be exported into a `std::shared_ptr<Attribute<T>>` that
can be handed back to the user. This allows client code to reuse the attribute data after the
destruction of any mesh object that was containing the attribute: only the
`std::shared_ptr<Attribute<T>>` needs to be kept alive.

<!-- @delete -->
```c++
// Delete and export a std::shared_ptr<Attribute<T>>
auto attr_ptr = mesh.delete_and_export_attribute<Scalar>("normals");

// Pass a raw pointer/span to the attribute data back to client code
auto data_ptr = attr_ptr->ref_all().data();
```

## Reserved Attribute Names

We use the convention that attribute names starting with `"$"` are reserved for internal use by the
mesh class. For example, `$vertex_to_position` and `$corner_to_vertex` are used for vertex positions
and facet indices respectively. The list of available internal attributes and their names is subject
to future changes.

## Attribute Policies

**Policies** can be used to control the behavior when manipulating attributes that wraps external
buffers, creating/deleting attributes with reserved names, etc. Policies are runtime properties that
need to be set for each attribute separately. They are copied over when an attribute is duplicated
via our copy-on-write mechanism.

### Create Policy

Controls the behavior when creating an attribute with a reserved name (starting with `$`). The
default is to throw an exception. See [reference documentation][Create policy] for more details.

### Copy Policy

Controls the behavior when copying an attribute that wraps an external buffer. By default, a deep
copy of the buffer will be created. See [reference documentation][Copy policy] for more details.

### Growth Policy

Controls the behavior when adding element to an attribute that wrap an external buffer. The default
behavior is to throw an exception. See [reference documentation][Growth policy] for more details.

```c++
Index dim = 3;
Index num_vertices = 10;
lagrange::SurfaceMesh<Scalar, Index> mesh(dim);

// Define external buffer
std::vector<Scalar> buffer(2 * num_vertices * dim);

// ... fill buffer with values ...

// Wrap external buffer AND resize num of vertices
mesh.wrap_as_vertices(buffer, num_vertices);

// Writable reference to vertex position attribute
auto& attr = mesh.ref_vertex_to_position();

// Set growth attribute policy
attr.set_growth_policy(lagrange::AttributeGrowthPolicy::ErrorIfExternal);
attr.set_growth_policy(lagrange::AttributeGrowthPolicy::AllowWithinCapacity);
attr.set_growth_policy(lagrange::AttributeGrowthPolicy::WarnAndCopy);

// Inserting more vertices might throw an error, depending on the policy
mesh.add_vertices(5);
```

### Write Policy

Controls the behavior when providing writable access to an attribute wrapping a const external
buffer. The default behavior is to throw an exception. See [reference documentation][Write policy]
for more details.

```c++
Index dim = 3;
Index num_vertices = 10;
lagrange::SurfaceMesh<Scalar, Index> mesh(dim);

// Define external buffer
const size_t num_channels = 3;
std::vector<Scalar> buffer(mesh.get_num_vertices() * num_channels);

// ... fill buffer with values ...

// Wrap external buffer as read-only attribute
auto id = mesh.wrap_as_const_attribute<Scalar>(
    "normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    num_channels,
    buffer);
auto& attr = mesh.ref_attribute<Scalar>(id);

// Set write policy for read-only attributes
attr.set_write_policy(lagrange::AttributeWritePolicy::ErrorIfReadOnly);
attr.set_write_policy(lagrange::AttributeWritePolicy::WarnAndCopy);

// Write access to the attribute might throw depending on policy
attr.ref(0) = 3.14;
```

### Delete Policy

Controls the behavior when deleting an attribute with a reserved name. The default behavior is to
throw an exception. See [reference documentation][Delete policy] for more details.

### Export Policy

Controls the behavior when exporting an attribute wrapping an external buffer. The default behavior
is to create an internal copy to ensure lifetime of the data is preserved. See [reference
documentation][Export policy] for more details.

```c++
Index dim = 3;
Index num_vertices = 10;
lagrange::SurfaceMesh<Scalar, Index> mesh(dim);

// Define external buffer
const size_t num_channels = 3;
std::vector<Scalar> buffer(mesh.get_num_vertices() * num_channels);

// ... fill buffer with values ...

// Wrap external buffer as read-only attribute
auto id = mesh.wrap_as_const_attribute<Scalar>(
    "normals",
    lagrange::AttributeElement::Vertex,
    lagrange::AttributeUsage::Normal,
    num_channels,
    buffer);

// Delete and export might create an internal copy depending on policy
using namespace lagrange;
auto attr_ptr1 = mesh.delete_and_export_attribute<Scalar>(
    "normals",
    AttributeDeletePolicy::ErrorIfReserved,
    AttributeExportPolicy::CopyIfExternal);
auto attr_ptr2 = mesh.delete_and_export_attribute<Scalar>(
    "normals",
    AttributeDeletePolicy::ErrorIfReserved,
    AttributeExportPolicy::ErrorIfExternal);
auto attr_ptr3 = mesh.delete_and_export_attribute<Scalar>(
    "normals",
    AttributeDeletePolicy::ErrorIfReserved,
    AttributeExportPolicy::KeepExternalPtr);
```

[Attribute usage]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#ga35b5eb426384b257452ee0ffdb732c27
[Attribute iteration]: ../../../{{ dox_folder }}/group__group-surfacemesh-iterate.html
[Create policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#ga809dfcec94612491ec5be8bb8614ceab
[Growth policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#gaee0f51b5f793101c19bd6dede5db7a7a
[Write policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#ga3018d576f81897e1712c3601b9625cb9
[Export policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#gade3ae5b7e72e9d4f92f29c6563551c10
[Delete policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#gad17b213b11e78aeb807ad3ece7e67e84
[Copy policy]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr.html#ga450ef027eac01dd93a89a15ff55de63f
