<!-- $ignore -->

# Entity Component System (Ecs)

For more information about the ECS architecture, see:

- [What you need to know about ECS](https://medium.com/ingeniouslysimple/entities-components-and-systems-89c31464240d) for quick overview
- [Overwatch Gameplay Architecture - GDC Talk](https://www.youtube.com/watch?v=W3aieHjyNvw) for a good example of usage and design considerations.
- [entt Crash Course](https://github.com/skypjack/entt/wiki/Crash-Course:-entity-component-system) for overview of the underlying `entt` library
- [ECS Back and Forth](https://skypjack.github.io/2019-06-25-ecs-baf-part-4/) for more details about ECS design, in particular hierarchies
- [Unity ECS documentation](https://docs.unity3d.com/Packages/com.unity.entities@0.1/manual/index.html) for Unity's version of ECS

## Registry
The `Viewer` uses a `Registry` (alias for `entt::registry`) to store all entities and their data. To manipulate entities and their components directly, use the object:
```c++
auto & registry = viewer.registry();
```
`Viewer` class exposes API that simplifies interaction with the `Registry`, e.g. `Viewer::show_mesh`.

## Entity
Unique identifier - it's just that. It's used to identify a unique "object" or "entity". Lagrange UI defines a `Entity` alias. Internally implemented as `std::uint32_t`.

To create a new entity, use:
```c++
Entity new_entity = registry.create();
```

To destroy:
```c++
registry.destroy(entity);
```

## Components
Any data that is attached to an `Entity`. Uniquely identified by template typename `<T>` and `Entity`.

Components **don't have logic, that means no code**. They only store data and implicitly define behavior. Ideally, the components should be `structs` with no functions. However, it may be beneficial to have setters/getters as member functions in some cases.


To attach a component of type `MyComponent` to an entity :
```c++
// When it doesn't exist
registry.emplace<MyComponent>(entity, MyComponent(42))

// When it might exist already
registry.emplace_or_replace<MyComponent>(entity, MyComponent(42))
```

To retrieve a component:
```c++
// If it exists already
MyComponent & c = registry.get<MyComponent>(entity);

// If you're not sure it exists
MyComponent * c = registry.try_get<MyComponent>(entity);
//or
if(registry.has<MyComponent>()){
    MyComponent& c = registry.get<MyComponent>(entity);
}
```

### Tag Components

"Empty" components may be used to tag entities, e.g. `Selected`, `Hovered`, etc. These types however must have non-zero size:
```c++
struct Hidden {
    bool dummy;
}
```

## Systems

Systems are the logic of the application. They are defined as functions that iterate over entities that have specified components only.
For example, running this system:
```c++
registry.view<Velocity, Position>().each([](Entity e, Velocity & velocity, Transform & transform){
    transform.local = Eigen::Translation3f(velocity) * transform.local;
});
```
will iterate over all entities that have both `Velocity` and `Transform` and apply the velocity vector to the transform.


Lagrange UI defines `System` as alias to `std::function<void(Registry&)>`, that is, a function that does something with the `Registry`. Typically these will be defined as:
```c++
System my_system = [](Registry &w){
    w.view<Component1, Component2, ...>.each([](Entity e, Component1 & c1, Component2 & c2, ...){
        //
    });
};
```


## Context Variables

Systems **do not have data**. However, it's often useful to have some state associated with a given system, e.g. for caching. Sometimes it's useful that this state be shared among several systems. Instead of storing this state in some single instance of a component, we can use *context* variables. These can be thought of as *singleton* components - only one instance of a `Type` can exist at a given time.

`InputState` is such a *singleton* component. At the beginning of the frame, it is filled with key/mouse information, including last mouse position, mouse delta, active keybinds, etc.:
```c++
void update_input_system(Registry & registry){
    InputState & input_state =  registry.ctx_or_set<InputState>();
    input_state.mouse_pos = ...
    input_state.mouse_delta = ...
    input_state.keybinds.update(...);
}
```

It can then be used by any other system down the line:
```c++
void print_mouse_position(Registry & registry){
    const auto & input_state = registry.ctx<InputState>();

    lagrange::logger().info("Mouse position: {}", input_state.mouse_pos);
}
```

## Design Considerations

Rules to follow when designing components and systems:

- Components have no functions, only data
- Systems have no data
- State associated with systems is stored as context variable (`registry.ctx<T>()`)


