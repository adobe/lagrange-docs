<!-- $ignore -->

# Scene

The scene module provides a 3D scene representation that stores [surface meshes](../core/mesh.md)
    together with instances and transforms. Several instances can reference the same mesh without
    duplicating its geometry. The module provides two scene containers:

* `SimpleScene` supports meshes with instancing and transforms.
* `Scene` supports hierarchical scene graphs with nodes, cameras, lights and materials. It
closely mirrors the glTF 2.0 scene model.

## Build and Types

```cmake
lagrange_include_module(scene)
target_link_libraries(my_target PRIVATE lagrange::scene)
```

The examples below build on each other within each language. Start with this triangle:

=== "C++"

    ```c++
    #include <lagrange/SurfaceMesh.h>

    #include <cstdint>
    #include <utility>

    using Scalar = double;
    using Index = std::uint32_t;
    using Mesh = lagrange::SurfaceMesh<Scalar, Index>;

    Mesh mesh;
    mesh.add_vertex({0, 0, 0});
    mesh.add_vertex({1, 0, 0});
    mesh.add_vertex({0, 1, 0});
    mesh.add_triangle(0, 1, 2);
    ```

=== "Python"

    ```python
    import lagrange as la
    import numpy as np

    mesh = la.SurfaceMesh()
    mesh.vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    mesh.add_triangle(0, 1, 2)
    ```

## Simple Scenes: Meshes and Instances

Adding a mesh does **not** create an instance. Add a `MeshInstance` with a valid `mesh_index` to
place the mesh in the scene. Its transform maps mesh-local coordinates to world coordinates.
The default transform is the identity.

This example creates two instances of the same triangle mesh. The first instance places the
triangle at its original position, and the second instance is placed two units along the X-axis.

=== "C++"

    ```c++
    #include <lagrange/scene/SimpleScene.h>

    lagrange::scene::SimpleScene<Scalar, Index> simple;
    const Index simple_mesh_id = simple.add_mesh(mesh);

    lagrange::scene::MeshInstance<Scalar, Index> instance;
    instance.mesh_index = simple_mesh_id;
    const Index first_instance_id = simple.add_instance(instance);

    instance.transform.translation() << 2, 0, 0;
    const Index second_instance_id = simple.add_instance(instance);
    ```

=== "Python"

    ```python
    simple = la.scene.SimpleScene3D()
    simple_mesh_id = simple.add_mesh(mesh)

    instance = la.scene.MeshInstance3D()
    instance.mesh_index = simple_mesh_id
    first_instance_id = simple.add_instance(instance)

    translated = np.eye(4)
    translated[:3, 3] = [2, 0, 0]
    instance.transform = translated
    second_instance_id = simple.add_instance(instance)
    ```

There is one source mesh and two instances. Instance indices are **local indices associated with
the source mesh**: identify an instance by `(mesh_index, instance_index)`.

| Operation | C++ | Python |
| --- | --- | --- |
| Number of source meshes | `simple.get_num_meshes()` | `simple.num_meshes` |
| Instances of a source mesh | `simple.get_num_instances(mesh_id)` | `simple.num_instances(mesh_id)` |
| Total instance count | `simple.compute_num_instances()` | `simple.total_num_instances` |
| Read a source mesh | `simple.get_mesh(mesh_id)` | `simple.get_mesh(mesh_id)` |
| Edit a source mesh | `simple.ref_mesh(mesh_id)` | `simple.ref_mesh(mesh_id)` |
| Read an instance | `simple.get_instance(mesh_id, instance_id)` | `simple.get_instance(mesh_id, instance_id)` |
| Edit an instance | `simple.ref_instance(mesh_id, instance_id)` | `simple.ref_instance(mesh_id, instance_id)` |

## Full Scenes: Nodes and Transforms

A `Scene` stores resources in separate arrays (`meshes`, `materials`, `images`, `textures`,
`cameras`, and `lights`). `scene.add(resource)` returns an index into the corresponding array. Adding
a resource alone does not attach it to the hierarchy.

A `Node` can contain mesh instances, camera IDs, light IDs, and child node IDs. A
`SceneMeshInstance` references a mesh through its `mesh` field and materials through its `materials`
list. Unlike a simple-scene `MeshInstance`, it has no transform of its own: it uses its containing
node's transform.

### Building a Hierarchy

Create a root translated three units along the Y-axis, then attach two child nodes that share the triangle:

=== "C++"

    ```c++
    #include <lagrange/scene/Scene.h>

    lagrange::scene::Scene<Scalar, Index> scene;
    const auto scene_mesh_id = scene.add(mesh);

    lagrange::scene::Node root;
    root.name = "root";
    root.transform.translation() << 0, 3, 0;
    const auto root_id = scene.add(std::move(root));
    scene.root_nodes.push_back(root_id);

    for (int i = 0; i < 2; ++i) {
        lagrange::scene::Node child;
        child.transform.translation() << 2 * i, 0, 0;
        lagrange::scene::SceneMeshInstance placement;
        placement.mesh = scene_mesh_id;
        child.meshes.push_back(std::move(placement));
        const auto child_id = scene.add(std::move(child));
        scene.add_child(root_id, child_id);
    }
    ```

=== "Python"

    ```python
    scene = la.scene.Scene()
    scene_mesh_id = scene.add(mesh)

    root = la.scene.Node()
    root.name = "root"
    root.transform = np.eye(4, dtype=np.float32)
    root.transform[:3, 3] = [0, 3, 0]
    root_id = scene.add(root)
    scene.root_nodes.append(root_id)

    for i in range(2):
        child = la.scene.Node()
        child.transform = np.eye(4, dtype=np.float32)
        child.transform[:3, 3] = [2 * i, 0, 0]
        placement = la.scene.SceneMeshInstance()
        placement.mesh = scene_mesh_id
        child.meshes.append(placement)
        child_id = scene.add(child)
        scene.add_child(root_id, child_id)
    ```

`add_child` updates both the parent's `children` and the child's `parent`. It does not remove an
existing parent relationship or remove the child from `root_nodes`. Use it to attach an unattached
node; when reparenting, remove the old references as well. Keep the hierarchy acyclic and register
only parentless nodes in `root_nodes`. `scene.add(node)` does not register a root automatically.

IDs are array indices, not persistent handles. Erasing or reordering resources requires updating
all references to them. In C++, avoid holding references to array elements across additions that
may reallocate their storage; reacquire them by ID afterward.

### Local and World Transforms

`Node::transform` maps node-local coordinates to its parent's coordinates. For a child, its world
transform is `parent_world * child_local`, applied to column vectors. Translations occupy the last
column of a homogeneous 4×4 matrix.

Use the utility to accumulate ancestor transforms rather than interpreting a node's local transform
as a world transform:

=== "C++"

    ```c++
    #include <lagrange/scene/scene_utils.h>

    const auto second_child_id = scene.nodes[root_id].children[1];
    const auto world_from_child =
        lagrange::scene::utils::compute_global_node_transform(scene, second_child_id);
    // world_from_child.translation() is (2, 3, 0).
    ```

=== "Python"

    ```python
    second_child_id = scene.nodes[root_id].children[1]
    world_from_child = la.scene.compute_global_node_transform(scene, second_child_id)
    assert np.allclose(world_from_child[:3, 3], [2, 3, 0])
    ```

The utility traverses the parent chain on each call. If you cache world transforms, invalidate them
when a node or any ancestor changes.

## Materials and Other Resources

Materials use a glTF-style metallic-roughness PBR model. C++ currently calls this type
`MaterialExperimental`; Python exposes it as `Material`.

Assign a single red material to both child instances:

=== "C++"

    ```c++
    lagrange::scene::MaterialExperimental material;
    material.name = "red";
    material.base_color_value << 1, 0, 0, 1;
    material.metallic_value = 0.0f;
    material.roughness_value = 0.8f;
    const auto material_id = scene.add(std::move(material));

    for (const auto child_id : scene.nodes[root_id].children) {
        scene.nodes[child_id].meshes[0].materials.push_back(material_id);
    }
    ```

=== "Python"

    ```python
    material = la.scene.Material()
    material.name = "red"
    material.base_color_value = np.array([1, 0, 0, 1], dtype=np.float32)
    material.metallic_value = 0.0
    material.roughness_value = 0.8
    material_id = scene.add(material)

    for child_id in scene.nodes[root_id].children:
        scene.nodes[child_id].meshes[0].materials.append(material_id)
    ```

For multiple materials on one mesh, create a single-channel **facet** attribute named `material_id`
on the source mesh. Its values are **local slots** into that instance's `materials` list. For example,
if `placement.materials` is `[7, 2]`, a facet value of `0` selects `scene.materials[7]`, not
`scene.materials[0]`. Use the mesh's `Index` type for the attribute. See
[Mesh Attributes](../core/attributes.md) for attribute creation.

Other resource relationships are:

| Resource | How it is referenced |
| --- | --- |
| Image (`ImageExperimental` in C++, `Image` in Python) | `Texture.image` indexes `scene.images`; an image stores pixel data or an external `uri` relative to the scene file |
| Texture | A material's `TextureInfo.index` indexes `scene.textures`; `TextureInfo.texcoord` selects a UV set, usually the mesh attribute `texcoord_0` |
| Camera | `Node.cameras` contains indices into `scene.cameras` |
| Light | `Node.lights` contains indices into `scene.lights` |

Adding images, textures, cameras, or lights to their scene arrays is not sufficient:
they need to be referenced by other scene elements as shown above.
Textured meshes need UV attributes with `AttributeUsage::UV`. Camera and
light coordinates are relative to the node that contains them. C++ camera view and projection
helpers are in `lagrange::scene::utils` in `scene_utils.h`.

## Converting Scenes and Meshes

Choose whether to preserve instancing or bake it into geometry:

| Function | Result |
| --- | --- |
| `mesh_to_simple_scene` / `meshes_to_simple_scene` | Simple scene with one identity instance per input mesh |
| `mesh_to_scene` / `meshes_to_scene` | Full scene with one identity instance per input mesh |
| `simple_scene_to_meshes` / `scene_to_meshes` | One transformed mesh per instance |
| `simple_scene_to_mesh` / `scene_to_mesh` | All transformed instances concatenated into one mesh |
| `scene_to_simple_scene` | Shared meshes and accumulated world-space instances, without the hierarchy or scene resources such as materials, textures, cameras, and lights |
| `simple_scene_to_scene` | Shared meshes and one child node per instance under a new root |

The last two functions operate on 3D scenes. Converting a full scene to a simple scene and
back does not restore the original hierarchy or metadata.

### Baking Instance Transforms

=== "C++"

    ```c++
    #include <lagrange/scene/scene_convert.h>
    #include <lagrange/scene/simple_scene_convert.h>

    const auto simple_meshes = lagrange::scene::simple_scene_to_meshes(simple);
    const auto simple_merged = lagrange::scene::simple_scene_to_mesh(simple);
    const auto merged = lagrange::scene::scene_to_mesh(scene);
    const auto geometry_scene = lagrange::scene::scene_to_simple_scene(scene);
    const auto flat_hierarchy = lagrange::scene::simple_scene_to_scene(geometry_scene);
    ```

=== "Python"

    ```python
    simple_meshes = la.scene.simple_scene_to_meshes(simple)
    simple_merged = la.scene.simple_scene_to_mesh(simple)
    merged = la.scene.scene_to_mesh(scene)
    geometry_scene = la.scene.scene_to_simple_scene(scene)
    flat_hierarchy = la.scene.simple_scene_to_scene(geometry_scene)

    assert merged.num_vertices == 6
    assert merged.num_facets == 2
    assert np.allclose(merged.vertices.min(axis=0), [0, 3, 0])
    assert np.allclose(merged.vertices.max(axis=0), [3, 4, 0])
    ```

These conversions leave the input scene unchanged. Meshes without instances do not contribute to
baked geometry. Concatenation duplicates geometry for each instance; it does not weld coincident
vertices. Prefer keeping instances when processing the shared source geometry is sufficient.

The `*_to_mesh` functions preserve shared mesh attributes by default; set `preserve_attributes` to
`false` in C++ or `False` in Python to disable this. This does not preserve the scene's resource
arrays in the resulting mesh.

Transforms also affect normal, tangent, and bitangent attributes. C++ accepts
`lagrange::TransformOptions`; Python exposes the corresponding `normalize_normals`,
`normalize_tangents_bitangents`, and `reorient` keyword arguments. Normalization is enabled by
default. For mirrored instances, set `reorient` to true if you want to reverse facet orientations
and flip normals, tangents, and bitangents for negative-determinant transforms; its default is false.

### Keeping Material Assignments

Use `scene_to_meshes_and_materials` when you need transformed geometry and its material IDs:

Per-facet material remapping requires [Lagrange 6.47.0 or later](https://github.com/adobe/lagrange/releases/tag/v6.47.0).
Earlier releases return the per-instance material lists but do not create or remap the output
`material_id` facet attribute as described below.

=== "C++"

    ```c++
    #include <cassert>

    const auto result = lagrange::scene::scene_to_meshes_and_materials(scene);
    const auto& placed_meshes = result.meshes;
    const auto& material_ids = result.material_ids;
    for (size_t i=0; i<placed_meshes.size(); ++i) {
        const auto& mesh = placed_meshes[i];
        for (auto mat_id : material_ids[i]) {
            const auto& material = scene.materials[mat_id];
            assert(material.name == "red");
        }
    }
    ```

=== "Python"

    ```python
    placed_meshes, material_ids = la.scene.scene_to_meshes_and_materials(scene)
    assert material_ids == [[material_id], [material_id]]
    for mesh, mat_ids in zip(placed_meshes, material_ids):
        assert np.all(mesh.attribute("material_id").data == material_id)
        for mat_id in mat_ids:
            material = scene.materials[mat_id]
            assert material.name == "red"
    ```

Each output mesh has a `material_id` facet attribute with **global** indices into `scene.materials`.
This differs from the source mesh's instance-local slots. `scene_to_meshes` performs the same
remapping. Facets with no material receive `lagrange::invalid<Index>()` (`la.invalid_index` in
Python). The separate `material_ids[i]` list identifies the materials referenced by the instance;
use the facet attribute for the exact facet-to-material assignment. Keep the scene's material,
texture, and image arrays if you need to interpret these IDs.

## Loading and Saving

Use the io module to load a full scene or a simple scene. The generic scene saver supports
`.gltf`, `.glb`, and `.obj`. Full-scene loading supports `.gltf`, `.glb`, `.fbx`, `.obj`,
and Lagrange's `.lgm`/`.lgs` formats. Additional import formats require building with
`LAGRANGE_WITH_ASSIMP=ON` (default: `OFF`) and depend on the importers enabled in Assimp.

The following saves the full-scene example and reloads it with polygon triangulation enabled:

=== "C++"

    ```c++
    #include <lagrange/io/load_scene.h>
    #include <lagrange/io/save_scene.h>

    lagrange::io::SaveOptions save_options;
    save_options.embed_images = true;
    lagrange::io::save_scene("scene.glb", scene, save_options);

    lagrange::io::LoadOptions load_options;
    load_options.triangulate = true;
    const auto loaded = lagrange::io::load_scene<
        lagrange::scene::Scene<Scalar, Index>>("scene.glb", load_options);
    ```

=== "Python"

    ```python
    la.io.save_scene("scene.glb", scene, embed_images=True)
    loaded = la.io.load_scene("scene.glb", triangulate=True)
    loaded_mesh = la.scene.scene_to_mesh(loaded)
    assert loaded_mesh.num_facets == merged.num_facets
    assert np.allclose(loaded_mesh.vertices.min(axis=0), [0, 3, 0])
    assert np.allclose(loaded_mesh.vertices.max(axis=0), [3, 4, 0])
    ```

For geometry-only I/O, C++ provides `load_simple_scene<SimpleSceneType>` and `save_simple_scene` in
`lagrange/io/load_simple_scene.h` and `lagrange/io/save_simple_scene.h`. Python provides
`la.io.load_simple_scene` and `la.io.save_simple_scene`. Use a full scene when you need
materials and other scene resources.

`LoadOptions::search_path` (Python: `search_path`) controls where related files such as `.mtl`,
`.bin`, and images are searched for; by default this is the input file's directory. Image loading is
controlled by `load_images`. For export, `embed_images` requests embedded images when supported by
the format.

!!! warning "Format limitations"
    OBJ does not preserve the node hierarchy, cameras, or lights. Its material export approximates
    PBR materials with a Phong model and may produce companion `.mtl` and texture files.

    The glTF and GLB formats do not support non-triangular facets.
    Check the export warnings: not all mesh attribute types or
    scene features are supported by every format.

    For lossless export/import of a full scene, use Lagrange's native `.lgm` or `.lgs` formats.

## API Reference

The public headers describe the full C++ API:

- [SimpleScene.h](https://github.com/adobe/lagrange/blob/main/modules/scene/include/lagrange/scene/SimpleScene.h): simple scenes and mesh instances.
- [Scene.h](https://github.com/adobe/lagrange/blob/main/modules/scene/include/lagrange/scene/Scene.h): nodes and scene resources.
- [simple_scene_convert.h](https://github.com/adobe/lagrange/blob/main/modules/scene/include/lagrange/scene/simple_scene_convert.h) and [scene_convert.h](https://github.com/adobe/lagrange/blob/main/modules/scene/include/lagrange/scene/scene_convert.h): geometry and scene conversions.
- [scene_utils.h](https://github.com/adobe/lagrange/blob/main/modules/scene/include/lagrange/scene/scene_utils.h): world transforms and camera utilities.
