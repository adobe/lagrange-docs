<!-- $ignore -->

# Mesh Visualization

## Geometry loading and registration

### Loading mesh

Creates and entity that represents the mesh. This entity is only a resource - it is not rendered.
It can be referenced by components that need this geometry for rendering/picking/etc.
These entities have `MeshData` component attached that contains a `lagrange::MeshBase` pointer.

```c++
ui::Entity mesh_from_disk = ui::load_mesh(registry, path);
ui::Entity mesh_from_memory = ui::register_mesh(registry, lagrange::create_sphere());
```

### Retrieving and interacting with the mesh

To retrieve a mesh:
```c++
MeshType & mesh = ui::get_mesh<MeshType>(registry, mesh_entity);
```

There are several methods that do not require the knowledge of the mesh type. These may however
incur copy and conversion costs.
```c++
RowMajorMatrixXf get_mesh_vertices(const MeshData& d);
RowMajorMatrixXf get_mesh_facets(const MeshData& d);
bool has_mesh_vertex_attribute(const MeshData& d, const std::string& name);
bool has_mesh_facet_attribute(const MeshData& d, const std::string& name);
...
RowMajorMatrixXf get_mesh_vertex_attribute(const MeshData& d, const std::string& name);
RowMajorMatrixXf get_mesh_facet_attribute(const MeshData& d, const std::string& name);
...
std::optional<RayFacetHit> intersect_ray(const MeshData& d, const Eigen::Vector3f& origin, const Eigen::Vector3f& dir);
...
```

### Loading scene

Loads a scene using Assimp. Creates a hierarchy of entities and loads meshes, materials and
textures. Returns the top-level entity.

```c++
ui::Entity root = ui::load_scene(registry, path);
```

To iterate over the scene, see the [`Tree` component](components.md#tree).

## Adding geometry to scene

### Default Physically Based Render (PBR)

Adds previously registered mesh geometry to the scene. This mesh will be rendered using PBR.

```c++
ui::Entity scene_object = ui::show_mesh(registry, mesh_entity);
```

Uses `DefaultShaders::PBR` shader.

See [Materials](mesh-visualization.md#materials) section to see how to control the appearance.

### Mesh visualizations

Adds a visualization of a mesh. {% if is_corp %} Designed after the discussion
[here](https://git.corp.adobe.com/lagrange/lagrange-lib/issues/194). {% endif %}

```c++
auto vertex_viz_entity = ui::show_vertex_attribute(registry, mesh_entity, attribute_name, glyph_type);
auto facet_viz_entity = ui::show_facet_attribute(registry, mesh_entity, attribute_name, glyph_type);
auto corner_viz_entity = ui::show_corner_attribute(registry, mesh_entity, attribute_name, glyph_type);
auto edge_viz_entity = ui::show_edge_attribute(registry, mesh_entity, attribute_name, glyph_type);
```

These functions will create a new scene object and render the supplied attribute using the selected glyph type.

#### `GlyphType::Surface`

Renders unshaded surface with color mapped from the supplied attribute. Supports attributes of dimension: 1, 2, 3, and 4.

- *Normalization*: The attribute value is automatically remapped to (0,1) range. To change the
  range, use `ui::set_colormap_range`
- *Colormapping*: By default, the attribute is interpreted as R, RG, RGB or RGBA value. To use
  different mapping, refer to [Colormaps](#colormaps) section.

#### Colormaps

If the glyph or shader supports colormapping, use the following function to set the colormap:

To use on of the default colormaps:
```c++
ui::set_colormap(registry, entity, ui::generate_colormap(ui::colormap_magma))
```
Or generate your own
```c++
ui::set_colormap(registry, entity, ui::generate_colormap([](float t){
    return Color(
        //... function of t from 0 to 1
    );
}));
```

Default colormaps:
```
colormap_viridis
colormap_magma
colormap_plasma
colormap_inferno
colormap_turbo
colormap_coolwarm
```


<!--
Glyph Categories
- Color Output
- Geometry Output
- Texture Output

Glyph types:
-  `GlyphType::Surface`
   -  Dimension = 3
   -  Vertex/Facet/Corner/Edge
   -  Output = Color
-  `GlyphType::RGBA`
   -  Dimension = 4
   -  Vertex/Facet/Corner/Edge
   -  Output = Color
-  `GlyphType::Sphere`
   -  Dimension = 1
   -  Vertex
   -  Output = Geometry (position + size + Color)
-  `GlyphType::EigenEllipsoid`
   -  (Not a priority, only if we need tensor visualization)
   -  Dimension = 3x3
   -  Vertex/Facet
   -  Output = Geometry (frame + Color)
-  `GlyphType::Arrow`
   -  Dimension = 3
   -  Vertex/Facet/Corner/Edge
   -  (Possible options: normalization)
   -  Output = Geometry (position + Vector3 + Color)
-  `GlyphType::Colormap`
   -  Dimension = 1
   -  Vertex/Facet/Corner/Edge
   -  (Possible options: which colormap)
   -  Output = Color
-  `GlyphType::Parametrization`
   -  Dimension = 2
   -  (Vertex?)/Corner
   -  Output = Texture
-  `...`
-->

## Materials

Any entity with `MeshRender` component has a `Material` associated with it (`MeshRender::material`).

To get a reference to entity's material, use:

```c++
std::shared_ptr<Material> material_ptr = ui::get_material(r, entity_with_meshrender);
```

Similarly, you may set a new material:
```c++
ui::set_material(r, entity_with_mesh_render, std::make_shared<ui::Material>(r, DefaultShaders::PBR);
```

### Color/Texture Material Properties

You may set colors and textures of materials using the following API:

```c++
auto & material = *ui::get_material(r, entity_with_meshrender);

//Sets "property name" to a red color
material.set_color("property name", ui::Color(1,0,0));

//Sets "texture name" to texture loaded from file
material.set_texture("texture name", ui::load_texture("texture.jpg"));
```

#### PBRMaterial
For the default `PBRMaterial`, you may use aliases for the property names:
```c++

//Uniform rgba color
material.set_color(PBRMaterial::BaseColor, ui::Color(1,0,0,1));
//RGB(A) color/albedo texture
material.set_texture(PBRMaterial::BaseColor, ui::load_texture("color.jpg"));

//Normal texture (and texture only)
material.set_texture(PBRMaterial::Normal, ui::load_texture("normal.jpg"));

//Uniform roughness
material.set_float(PBRMaterial::Roughness, 0.75f);
//Roughness texture
material.set_texture(PBRMaterial::Roughness, ui::load_texture("metallic.jpg"));

//Uniform roughness
material.set_float(PBRMaterial::Metallic, 0.75f);
//Metallic texture
material.set_texture(PBRMaterial::Metallic, ui::load_texture("metallic.jpg"));

//Uniform opacity
material.set_float(PBRMaterial::Opacity, 1.0f);
//Opacity texture
material.set_texture(PBRMaterial::Opacity, ui::load_texture("opacity.jpg"));
```

### Rasterizer Properties

To control OpenGl properties, you may following syntax:

```c++
material.set_int(RasterizerOptions::PolygonMode, GL_LINE);
material.set_float(RasterizerOptions::PointSize, PointSize);
```

See `<lagrange/ui/Shader.h>` for a list of supported `RasterizerOptions`;

### Custom Shader Properties

You may set arbitrary `int` or `float` or `Color` or `Texture` to the material. It will be set as a
shader uniform if it exists in the shader, otherwise there will be no effect.
