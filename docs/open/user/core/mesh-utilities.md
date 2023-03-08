# Mesh Utility Functions

This page describes various mesh and attribute utilities available in Lagrange's core module.

## Compute Mesh Normals

As described in our [Mesh Utilities][mesh-utils] page, mesh normals can be computed using on of the
following function:

```c++
#include <lagrange/compute_normal.h>
#include <lagrange/compute_facet_normal.h>
#include <lagrange/compute_vertex_normal.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;

// Compute per-facet normals
lagrange::FacetNormalOptions facet_options;
auto fid = compute_facet_normal(mesh, facet_options);

// Compute per-vertex normals using a uniform weight for each incident triangle
VertexNormalOptions vertex_options;
vertex_options.weight_type = lagrange::NormalWeightingType::Uniform;
auto vid = compute_vertex_normal(mesh, vertex_options);

// Compute indexed per-corner normals. Edges with a dihedral
// angle smaller than π/2 will be considered smooth
Scalar angle_threshold_rad = M_PI * 0.5;
auto cid = compute_normal(mesh, angle_threshold_rad);
```

See [Mesh Utilities][mesh-utils] reference documentation for more details.

## Compute Tangent Space

{% if is_corp %}
![Test mesh with tangent-space information](../../../corp/user/core/img/tangent_bitangent.png){width="300"}
{% endif %}

Lagrange offers a function to compute tangent-space information, following [@Mikkelsen:2008:SOW]:

```c++
#include <lagrange/compute_tangent_bitangent.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;
lagrange::TangentBitangentOptions options;

// Pad the 4th channel of the output attributes with
// a ±1 indicating the sign of the UV triangle
options.pad_with_sign = true;

auto btn = compute_tangent_bitangent(mesh, options);
btn.tangent_id; // id of the generated tangent vector attribute
btn.bitangent_id; // id of the generated bitangent vector attribute
```

The input mesh must have an existing indexed UV and normal attribute. The
`options.output_element_type` can be either `Indexed` (default), or `Corner`:

- If the output type is `Corner`, no averaging is performed, and the output attribute contains
  directly the per-corner tangent space.
- If the output type is `Indexed`, averaging is performed based on the provided indexed attributes.
  Corners with identical normals and UVs will be considered as a single smoothing group for tangent
  space computation.

<figure markdown="1">
  <div style="display:flex">
    <div>
      <img src="../../core/img/tangent_groups.png" width=500>
    </div>
  </div>

  <figcaption markdown="1">Corners are grouped into different smoothing groups, based on provided
  UV and normal attributes. Image from [@Mikkelsen:2008:SOW]</figcaption>
</figure>

!!! info "Accuracy vs Mikktspace"
    We have [unit
    tests](https://github.com/adobe/lagrange/blob/e69058be8153d0a600e3e073740a93cd972da89c/modules/core/tests/test_compute_tangent_bitangent.cpp#L382-L385)
    comparing our results with the original [mikktspace](https://github.com/mmikk/MikkTSpace) code [@Mikkelsen:2008:SOW]. We found that, in
    floating points, we have a max error of `1e-6f`.

!!! info "Performance vs Mikktspace"
    Our
    [benchmark](https://github.com/adobe/lagrange/blob/e69058be8153d0a600e3e073740a93cd972da89c/modules/core/tests/test_compute_tangent_bitangent.cpp#L471)
    shows that we are 5x-6x faster than mikktspace, mostly due to the addition of multithreading.

!!! tip "Welding Attributes"
    The original mikktspace code expects the input UV/normals as a per-corner value, and will always
    weld corners sharing identical UV/normal values. In contrast, our mesh data structure uses a
    more generic indexed attribute, and we use an attribute's index to identify and group together
    identical corners.

    In practice, this means that you will need to weld together any identical attribute that do not
    share the same indices, or you may end up with different result compared to mikktspace.

!!! warning "Limitations: Triangle Meshes vs Quad Meshes"
    - Our code for averaging tangent vectors only support triangle meshes at the moment.
    - Quad meshes and quad-dominant meshes can be used, but only with `output_element_type = Corner` (no averaging will be performed).
    - General polyhedral facets (with > 4 vertices) are not supported at the moment.

## Normalize Meshes

Meshes can be normalized to fit in a unit box centered at the origin using the `normalize_meshes()`
function, which modifies the mesh in place:

```c++
#include <lagrange/normalize_meshes.h>

// Normalize a single mesh
normalize_mesh(mesh);

// Normalize a list of meshes using the same transform for all meshes
using MeshType = SurfaceMesh32f;
std::vector<MeshType *> meshes;
meshes.push_back(&mesh1);
meshes.push_back(&mesh2);
meshes.push_back(&mesh3);
normalize_meshes(meshes);
```

<!-- Note: We should add a initializer list overload to `normalize_meshes()` ... :) -->

See: [Mesh Utilities][mesh-utils] documentation.

## Triangulate Polygonal Facets

A mesh with polygonal facets can be turned into a pure triangle mesh by calling the following code:

```c++
#include <lagrange/triangulate_polygonal_facets.h>

// Modifies the mesh in place
triangulate_polygonal_facets(mesh);
```

Under the hood we use [Mapbox's Earcut](https://github.com/mapbox/earcut.hpp) implementation for
polygonal facets with 5 vertices or more.

See: [Mesh Utilities][mesh-utils] documentation.

## Transfer Mesh Attributes

Attributes can be mapped from one type of mesh element to another using the
[`map_attribute()`][attr-utils] functions.

```c++
#include <lagrange/compute_normal.h>
#include <lagrange/map_attribute.h>

// Transfer vertex normal attribute onto mesh facets (values will be averaged)
auto vid = compute_vertex_normals(mesh);
auto fid = map_attribute(mesh, vid, "new_name", lagrange::AttributeElement::Facet);
```

One can also transfer an attribute type in place (i.e. without creating a new attribute, just
replacing the old one):

```c++
#include <lagrange/compute_normal.h>
#include <lagrange/map_attribute.h>

// Transfer vertex normal attribute onto mesh facets (values will be averaged)
auto id = compute_vertex_normals(mesh);
map_attribute_in_place(mesh, id, lagrange::AttributeElement::Facet);
auto &attr = mesh.get_attribute<Scalar>(id);
assert(attr.get_element_type() == lagrange::AttributeElement::Facet);
```

Transferring attributes from any element type to any other type is supported. The values will either
be <span style="color:navy">**dispatched**</span> or <span style="color:maroon">**gathered**</span>
depending on the type of operation, as summarized below:


| Source\Target | Vertex   | Facet    | Edge     | Corner   | Indexed  | Value    |
|---------------|----------|----------|----------|----------|----------|----------|
| Vertex        |   ∅      | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Facet         | <span style="color:maroon">Gather</span>  |    ∅     | <span style="color:maroon">Gather</span>  | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Edge          | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  |    ∅     | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Corner        | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  |    ∅     | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Index         | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  | <span style="color:maroon">Gather</span>  | <span style="color:navy">Dispatch<span> |    ∅     | <span style="color:navy">Dispatch<span> |
| Value         | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |    ∅     |


!!! example
    - Transfering a vertex attribute to mesh corner elements is a _dispatch_ operation, and will not
    modify any value.
    - Transfering a corner attribute to mesh vertex elements is an _gather_ operation, and
    numerical values will be averaged.

!!! note "Value Attributes"
    When transfering a value attribute to any other type of element, it is expected that the number
    of entries in the source attribute matches the target number of mesh element.

    Conversely, transferring from any other mesh element type to a value attribute will create a
    buffer with the same number of entries as the input attribute element type.

!!! note "Indexed Attributes and Value Attributes"
    When transfering a value attribute to an indexed attribute (and vice-versa), the value attribute
    is expected to have a number of elements equals to the number of _mesh corners_.

    - Transfering `Value` -> `Indexed` will create an indexed attribute with a trivial index buffer
    (identity mapping corner $c_i$ $\to$ value $i$).
    - Transfering `Indexed` -> `Value` will interpret the indexed attribute as if it were a corner
    attribute. The indexing will be lost on conversion.

See: [Attributes Utilities][attr-utils] documentation.

## Unify Index Buffers

It is possible to unify various indexed attributes so they can share the same index buffer. This is
especially useful for rendering, e.g. to turn a mesh with different indexing for normals, uv, etc.
into something suitable for the GPU.

```c++
#include <lagrange/unify_index_buffer.h>

// Using attribute id to identify indexed attribute to unify
auto unified_mesh = unify_index_buffer(mesh, {normal_id, uv_id});

// Using attribute names instead
auto unified_mesh = unify_index_buffer(mesh, {"normals", "uv"});
```

!!! note "Vertex Indices"
    The output mesh will use a unified index buffer for both vertex positions and the provided
    indexed attributes. As a result, some vertices might be duplicated (e.g. if two incident corners
    have different normals, or a UV seam).

See: [Attributes Utilities][attr-utils] documentation.

[attr-utils]: ../../../{{ dox_folder }}/group__group-surfacemesh-attr-utils.html
[mesh-utils]: ../../../{{ dox_folder }}/group__group-surfacemesh-utils.html

## Connected Components

Connected components can be computed via the [compute_components()][compute-components] function:

```c++
#include <lagrange/compute_components.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;

// Consider facets to be connected if they are touching by a common vertex
lagrange::ComponentOptions options;
options.connectivity_type = lagrange::ComponentOption::ConnectivityType::Vertex;

// Compute connected components as a per-facet attribute
auto num_components = lagrange::compute_components(mesh, options);
auto &component_id = mesh.get_attribute<Index>(mesh, options.output_attribute_name).get_all();

for (Index f = 0; f < mesh.get_num_facets(); ++f) {
    assert(0 <= component_id[f] && component_id[f] < num_components);
}
```

You can choose between edge-connected and vertex-connected components via the
`options.connectivity_type` parameter.

[compute-components]: ../../../{{ dox_folder }}/group__group-surfacemesh-utils.html#gafedc8c0d66af62d6f3d540465c0018c6

## Combine Meshes

It is possible to combine multiple meshes into a single aggregated mesh via the
[combine_meshes()][combine-meshes] function. This function preserves attributes by default, unless
called with `preserve_attributes = false`. When preserving input mesh attributes, all attributes in
the input meshes must be compatible (i.e. all meshes share the same attributes, with the same
type/number of channels, etc.).

```c++
#include <lagrange/combine_meshes.h>

lagrange::SurfaceMesh<Scalar, Index> mesh1, mesh2, mesh3;

// Call via initializer list of mesh pointers
auto aggregate_mesh1 = lagrange::combine_meshes({&mesh1, &mesh2, &mesh3});

// Call via an array of meshes (meshes are shallow-copied in this example)
constexpr size_t num_meshes = 3;
std::array<const SurfaceMesh<Scalar, Index>, num_meshes> mesh_list = {
    mesh1,
    mesh2,
    mesh3};
auto aggregate_mesh2 = lagrange::combine_meshes(mesh_list);

// Call via generic callbacks
auto aggregate_mesh3 = lagrange::combine_meshes(num_meshes,
    [](size_t idx) -> const SurfaceMesh<Scalar, Index> & {
      return mesh_list[idx];
    });
```

[combine-meshes]: ../../../{{ dox_folder }}/group__group-surfacemesh-utils.html#ga363707c2e65474638292c738c072868c

## Vertex Valence

Vertex valence can be computed using the [compute_vertex_valence()][compute-vertex-valence]
function:

```c++
#include <lagrange/compute_vertex_valence.h>
#include <lagrange/views.h>
#include <lagrange/Logger.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;

// Compute vertex valence as a per-vertex attribute
auto id = lagrange::compute_vertex_valence(mesh);

// Count regular vertices using a Eigen::Map view of the attribute
vertex_valence = attribute_vector_view<Index>(mesh, id);
auto num_regular_vertices = (vertex_valence.array() == 6).count();

lagrange::logger().info("The mesh has {} regular vertices", num_regular_vertices);
```

[compute-vertex-valence]: ../../../{{ dox_folder }}/group__group-surfacemesh-utils.html#ga6a2a7d7f5165ef7f5433ef67efad4306

## Adjacency Graph

While our mesh class offers some low-level [navigation
methods](mesh.md#connectivity-and-navigation), sometimes it beneficial to operate on an explicit
adjacency list representation of a connectivity graph. Currently we offer the function
[compute_vertex_vertex_adjacency()][compute-vertex-vertex-adjacency] to compute the corresponding
adjacency list graph:

```c++
#include <lagrange/compute_vertex_vertex_adjacency.h>

lagrange::SurfaceMesh<Scalar, Index> mesh;

// Build adjacency list representation of the vertex-vertex connectivity graph
auto graph = lagrange::compute_vertex_vertex_adjacency(mesh);

// Display all edges of the graph
assert(graph.get_num_entries() == mesh.get_num_vertices());
for (Index x = 0; x < mesh.get_num_vertices(); ++x) {
    lagrange::logger().info("Vertex v{} has {} neighbors", x, graph.get_num_neighbors(x));
    for (Index y : graph.get_neighbors(x)) {
        lagrange::logger().info("Edge v{} -> v{}", x, y);
    }
}
```

!!! note "Connectivity & Edge Information"
    While our [mesh navigation](mesh.md#connectivity-and-navigation) methods require the user to
    call `mesh.initialize_edges()` beforehand, `compute_vertex_vertex_adjacency()` does not have
    such a requirement, and will compute vertex-vertex connectivity information directly.

[compute-vertex-vertex-adjacency]: ../../../{{ dox_folder }}/group__group-surfacemesh-utils.html#ga203af050581e879b52d339558b788a08
