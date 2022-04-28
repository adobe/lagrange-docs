<!-- $ignore -->

# UI Module

Lagrange UI module is a mini 3D engine C++ library built on top of `EnTT`.

## Prerequistes

Must have `OpenGL 3.3` capable drivers and a windowing system (headless is not supported). To use
the library, enable `LAGRANGE_MODULE_UI` in CMake and

```c++
#include <lagrange/ui/UI.h>
namespace ui = lagrange::ui;
```

## Overview

Lagrange UI uses an **Entity-Component-System (ECS)** architecture:

- Entity is a unique identifier
- Components define data and behavior (but no logic)
- Systems define logic (but no data).

See [**ECS implementation section**](ecs.md) for more information about ECS and how it's implemented
in Lagrange UI. The underlying library for ECS is [`EnTT`](https://github.com/skypjack/entt).

The entry point to the library is the `Viewer` class. It instantiates a window and owns a `Registry`
instance and `Systems` instance. `Registry` contains all the data (entities and components) and
`Systems` contain all the behavior (sequence of functions that is called every frame). To start the
UI:

```c++
ui::Viewer viewer;
viewer.run([](){
    //Main loop code
});

//Or

viewer.run([](ui::Registry & r){
    //Main loop code
    return should_continue_running;
});
```

The API to interact with the UI follows the pattern:
```c++
ui::Entity entity = ui::do_something(registry, params)
SomeData & data = registry.get<SomeData>(entity);
```

For example:
```c++
//Loads mesh from path
ui::Entity mesh_geometry = ui::load_mesh(registry, path);

//Adds the mesh to scene
ui::Entity mesh_visualization = ui::show_mesh(registry, mesh_geometry);

//Retrieves Transform component of the visualized mesh
Transform & transform = registry.get<Transform>(mesh_visualization);
```

All entities and their components live in a `Registry`. To access/set/modify the entities and
components, use the `Viewer::registry()`.
```c++
auto & registry = viewer.registry();
auto entity = registry.create();
registry.emplace<MyPositionComponent>(entity, MyPositionComponent(0,0,0));
```

!!! note
    You can use `Viewer` class as an argument instead of `Registry`, e.g.:
    ```c++
    Viewer v;
    auto mesh_geometry = ui::load_mesh(v, path);
    ```

## Further Documentation

[Doxygen generated documentation](../../{{ dox_folder }}/namespacelagrange_1_1ui.html)

