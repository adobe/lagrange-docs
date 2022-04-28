<!-- $ignore -->

# Customizing Lagrange UI

!!! warning
    This page is under construction In the meantime, refer to files named `default_{}` to see how
    the UI registers the default types and functionality.

## Components

You may add any time of component using `registry.emplace<ComponentType>(entity)`. However to enable
more advanced features, you may register the components in the UI:

`register_component<T>`
- enables reflection
- enables runtime add/clone/move of com ponents

`register_component_widget<T>`
- defines ImGui code to render
- enables drag-and-drop


## Tools

*TBD*

`register_element_type<E>` (Object/Facet/Edge/Vertex/...)

`register_tool<E,T>` (Select/Translate/Rotate/Scale/...)

## Geometry

Lagrange meshes must be registered to work. By default, only the `TriangleMesh3Df` and
`TriangleMesh3D` are registered.

`ui::register_mesh_type<MeshType>()`

## Rendering

### Shader and Material properties

Material properties can be defined in the shader using the following syntax:


```glsl
#pragma property NAME "DISPLAY NAME" TYPE(DEFAULT VALUE AND/OR RANGE) [TAG1, TAG2]
```

For example:
```glsl
//Defines a 2D texture property with the default value of rgba(0.7,0.7,0.7,1) if no texture is bound
#pragma property material_base_color "Base Color" Texture2D(0.7,0.7,0.7,1)
//Defines a 2D texture property with the default value of red=0.4 if no texture is bound
#pragma property material_roughness "Roughness" Texture2D(0.4)
//Defines a 2D texture property with the default value of red=0.1 if no texture is bound
#pragma property material_metallic "Metallic" Texture2D(0.1)
//Defines a 2D texture property that is to be interpreted as normal texture
#pragma property material_normal "Normal" Texture2D [normal]
//Defines a float property, with the default value of 1 and range 0,1
#pragma property material_opacity "Opacity" float(1,0,1)
```

The pragmas are parsed whenever a shader is loaded and replaced with:
```glsl
uniform TYPE NAME = DEFAULT_VALUE
```
In case of `Texture2D`, these uniforms are generated:
```glsl
uniform sampler2D NAME;
uniform bool NAME_texture_bound = false;
uniform VEC_TYPE NAME_default_value = DEFAULT_VALUE;
```
