# Mesh Utility Functions

This page describes various mesh and attribute utilities available in Lagrange's core module.

## Compute Mesh Normals

As described in our [Mesh Utilities][mesh-utils] page, normals can be computed using on of the
following function:

```c++
#include <lagrange/compute_normal.h>
#include <lagrange/compute_facet_normal.h>
#include <lagrange/compute_vertex_normal.h>

auto id = compute_facet_normal(mesh, options);
auto id = compute_vertex_normal(mesh, options);
auto id = compute_normal(mesh, options);
```

See: [Mesh Utilities][mesh-utils] documentation.

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

Under the hood we use [Mapbox's Earcut](https://github.com/mapbox/earcut.hpp) immplementation for
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
be <span style="color:navy">**dispatched**</span> or <span style="color:maroon">**averaged**</span>
depending on the type of operation, as summarized below:


| Source\Target | Vertex   | Facet    | Edge     | Corner   | Indexed  | Value    |
|---------------|----------|----------|----------|----------|----------|----------|
| Vertex        |   ∅      | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Facet         | <span style="color:maroon">Average</span>  |    ∅     | <span style="color:maroon">Average</span>  | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Edge          | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  |    ∅     | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Corner        | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  |    ∅     | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |
| Index         | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  | <span style="color:maroon">Average</span>  | <span style="color:navy">Dispatch<span> |    ∅     | <span style="color:navy">Dispatch<span> |
| Value         | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> | <span style="color:navy">Dispatch<span> |    ∅     |


!!! example
    - Transfering a vertex attribute to mesh corner elements is a _dispatch_ operation, and will not
    modify any value. - Transfering a corner attribute to mesh vertex elements is an _averaging_
    operation, and numerical changes will occur.

!!! note "Value Attributes"
    When transfering a value attribute to any other type of element, it is expected that the number
    of entries in the source attribute matches the target number of mesh element. When transfering a
    value attribute to an indexed attribute, the value buffer is expected to have the same number of
    elements as the number of mesh corners.

    Conversely, transferring from any other mesh element type to a value attribute will create a
    buffer with the same number of entries as the input attribute element type.

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
