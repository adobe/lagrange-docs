<!-- $ignore -->

# Legacy Mesh Attributes

!!! warning "Legacy Mesh"
    Since v6.0.0, Lagrange introduced a new [polygonal mesh](mesh.md) class that is meant to
    replace the original mesh class used throughout Lagrange. The old `lagrange::Mesh<>` class is
    thus **deprecated**, but will be kept around for a while until we can transition all our code to
    the new data structure.

Lagrange provides functions to compute some of the commonly used mesh
attributes.

## Vertex Attributes

### Normals

The following snippet shows how to compute [per-vertex normal][vertex normal]:

```c++
#include <lagrange/compute_vertex_normal.h>

lagrange::compute_vertex_normal(mesh);
assert(mesh.has_vertex_attribute("normal"));

const auto& vertex_normals =
    mesh.get_vertex_attribute("normal");
assert(vertex_normals.rows() == mesh.get_num_vertices());
assert(vertex_normals.cols() == 3);
```

!!! note
    The resulting vertex normals are stored as a vertex attribute named
    "normal".  Its size is `n` by `3`, where `n` is the number of vertices. In
    addition, this method only works for 3D mesh.

!!! example "Implementation details"
    The per-vertex normal is computed as the angle
    weighted average of facet normals.

[vertex normal]: https://en.wikipedia.org/wiki/Vertex_normal

### Vertex Valance

In graph theory, [vertex valance] is the number of edge incident at a vertex.

```c++
#include <lagrange/compute_vertex_valance.h>

lagrange::compute_vertex_valance(mesh);
assert(mesh.has_vertex_attribute("valance"));

const auto& valance =
    mesh.get_vertex_attribute("valance");
assert(valance.rows() == mesh.get_num_vertices());
assert(valance.cols() == 1);
```

!!! note
    The resulting vertex valance data is stored as a vertex attribute
    named "valance".  It is an `n` by `1` matrix, where `n` is the number of vertices.

[vertex valance]: https://en.wikipedia.org/wiki/Degree_(graph_theory)

## Facet Attributes

### Normals

The following snippet computes the per-facet normal:

```c++
#include <lagrange/compute_triangle_normal.h>

lagrange::compute_triangle_normal(mesh);
assert(mesh.has_facet_attribute("normal"));

const auto& facet_normals =
    mesh.get_facet_attribute("normal");
assert(facet_normals.rows() == mesh.get_num_facets());
assert(facet_normals.cols() == 3);
```

!!! note
    The output facet normal is stored as a `m` by `3` facet attribute
    named "normal", where `m` is the number of facets.

!!! warning "Limitation"
    For now, only 3D triangle normal computation is supported.


### Area

The following snippet computes the per-facet area:

```c++
#include <lagrange/compute_facet_area.h>

lagrange::compute_facet_area(mesh);
assert(mesh.has_facet_attribute("area"));

const auto& areas =
    mesh.get_facet_attribute("area");
assert(areas.rows() == mesh.get_num_facets());
assert(areas.cols() == 1);
```

!!! note
    The output facet area is stored as a `m` by `1` facet attribute named
    "area", where `m` is the number of facets.  Both triangle and quad facet types
    are supported.

### UV Distortion

UV distortion measures the amount of _skew_ introduced by a mesh's [UV mapping].

```c++
#include <lagrange/compute_uv_distortion.h>

lagrange::compute_uv_distortion(mesh);
assert(mesh.has_facet_attribute("distortion"));

const auto& distortion =
    mesh.get_facet_attribute("distortion");
assert(distortion.rows() == mesh.get_num_facets());
assert(distortion.cols() == 1);
```

!!! note
    The per-facet distortion is a `m` by `1` facet attribute named
    "distortion", where `m` is the number of facets.  The computation of distortion
    measure requires the input is triangular.  Small positive values indicate low
    distortion, and negative values indicate inverted triangle in UV space.

!!! example "Implementation details"
    This method computes the 2D conformal AMIPS energy
    defined in [Rabinovich et al. 2017].

[Rabinovich et al. 2017]: https://igl.ethz.ch/projects/slim/

[UV mapping]: https://en.wikipedia.org/wiki/UV_mapping


## Edge Attributes

### Edge Length

Edge length can be computed:

```c++
#include <lagrange/compute_edge_lengths.h>

lagrange::compute_edge_lengths(mesh);
assert(mehs.has_edge_attribute("length"));

const auto& edge_lengths =
    mesh.get_edge_attribute("length");
assert(edge_lengths.rows() == mesh.get_num_edges());
assert(edge_lengths.cols() == 1);
```

!!! note
    Edge lengths are stored as a `e` by `1` per-edge attribute named
    "length", where `e` is the number of undirected edges.

### Dihedral Angle

For _manifold_ meshes, [dihedral angle] is defined as the angle formed by the
normals of two adjacent facets.

```c++
#include <lagrange/compute_dihedral_angles.h>

lagrange::compute_dihedral_angles(mesh);
assert(mesh.has_edge_attribute("dihedral_angle"));

const auto& dihedral_angle =
    mesh.get_edge_attribute("dihedral_angle");
assert(dihedral_angle.rows() == mesh.get_num_edges());
assert(dihedral_angle.cols() == 1);
```

!!! note
    The computed dihedral angles are stored as a `e` by `1` edge
    attribute named "dihedral_angle", where `e` is the number of edges.  All angles
    are in radians.

!!! warning "Limitation"
    The dihedral angle is only well-defined for 3D _manifold_ meshes.

[dihedral angle]: http://mathworld.wolfram.com/DihedralAngle.html

