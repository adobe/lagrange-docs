<!-- $ignore -->

# User Interface

## User Interface Panels

UI Panels are implemented also as entities. Panels have the `UIPanel` component. The `UIPanel` components describes the ImGui information (panel title, position, etc.).

To create a new UI panel:
```c++
auto panel_entity = ui::add_panel(registry, "Title of the panel",[](){
    // Do NOT call Imgui::Begin()/End()
    Imgui::Text("Hello world");
});
//or
auto panel_entity = ui::add_panel(registry, "Title of the panel", [](Registry &registry, Entity e){
    //Entity e is the panel_entity
});
```

Example of multiple instances of a same "type" of panel:

```c++

struct MyPanelState { int x = 0; }

auto panel_fn = [](Registry &registry, Entity e){
    auto & state = registry.get_or_emplace<MyPanelState>(e);
    ImGui::InputInt("x", &state.x);
};

auto panel0 = ui::add_panel(registry,"panel with x = 0",panel_fn)
registry.emplace<MyPanelState>(panel0, MyPanelState{0})

auto panel1 = ui::add_panel(registry,"panel with x = 1",panel_fn);
registry.emplace<MyPanelState>(panel1, MyPanelState{1})

```

