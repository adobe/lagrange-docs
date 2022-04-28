<!-- $ignore -->

# Components
Entities can have several components that define their behavior. Here is a list of the common
components used throughout Lagrange UI.

## `Name`
Subclassed `std::string`. Acts as a display name. Will be shown in UI if it exists, otherwise a
generated name will be used. Does not have to be unique.

## `Transform`
Contains local and global transformations and a viewport transform.

```c++
// Translates entity one unit in X direction
ui::Transform & transform = registry.get<ui::Transform>(e);
transform.local = Eigen::Translation3f(1,0,0);
```

Global transformation is recomputed after each `Simulation` step. Only change the `local` transform.

## `Tree`
Defines scene tree relationship. Data is stored using `parent`, `first_child`, `previous_sibling`
and `next_sibling` entity IDs.

Use helper functions to query or change the tree structure, do not change directly (unless you know
what you're doing).
```c++
//Orphans entity and parents it under new_parent
ui::reparent(registry, entity, new_parent);

//Applies lambda to each direct child entity of parent
ui::foreach_child(registry, parent, [](Entity child){
    //...
});

//Applies lambda to each  child entity of parent, recursively
ui::foreach_child_recursive(registry, parent, [](Entity child){
    //...
});

//In-order traversal of scene tree
ui::iterate_inorder(registry, root, [](Entity current){
    //On Enter

    //Return true to continue to traverse children
    return true;
},[](Entity current){
    //On Exit
});

// See utils/treenode.h for more details
```

## `MeshGeometry`
Contains reference to geometry entity

```c++
MeshGeometry mg;
mg.entity = ..
```


## `Hovered` and `Selected`

These components acts as flags whether the entity is hovered or selected respectively.

Useful helper functions
```c++
bool is_selected(Registry &registry, Entity e);
bool is_hovered(Registry &registry, Entity e);
bool select(Registry& registry, Entity e);
bool deselect(Registry& registry, Entity e);
std::vector<Entity> collect_selected(const Registry& registry);
std::vector<Entity> collect_hovered(const Registry& registry);
//See `utils/selection.h` for details
```

## `Layer`

There are 256 layers an entity can belong to. The `Layer` component specifies which layers the
entity belongs to. Entity can belong to several layers at once. There are several default layers:

- `ui::DefaultLayers::Default` - everything belongs to it by default
- `ui::DefaultLayers::Selection` - selected entities
- `ui::DefaultLayers::Hover` - hovered entities

Default constructed `Layer` component belongs to `ui::DefaultLayers::Default`.

You can register your own layer by calling
```c++
ui::LayerIndex layer_index = ui::register_layer_name(r, "my layer name");
```

There are several utility functions for working with layers:
```c++
void add_to_layer(Registry&, Entity e, LayerIndex index);
void remove_from_layer(Registry&, Entity e, LayerIndex index);
bool is_in_layer(Registry&, Entity e, LayerIndex index);
bool is_in_any_layers(Registry&, Entity e, Layer layers_bitset);
bool is_visible_in(
    const Registry&,
    Entity e,
    const Layer& visible_layers,
    const Layer& hidden_layers);
```


## `UIPanel`
See [User Interface page](user-interface.md).

## `ViewportComponent`
See [Viewports page](viewports.md)
