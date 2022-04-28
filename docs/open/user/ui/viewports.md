<!-- $ignore -->

# Viewports

Viewports are implemented as entities with `ViewportComponent` component. Those referenced in `ViewportPanel` are rendered to screen, otherwise they are rendered off-screen. There is always one **focused** `ViewportPanel` (identified by the context variable `FocusedViewportPanel`).

See `components/Viewport.h` and `utils/viewport.h` for utility functions related to viewport, viewport panels and cameras.

## Entity visibility

Each `ViewportComponent` has `visible_layers` and `hidden_layers` that control which entities can be renderer in this viewport (see [`Layer` component](components.md#layer) for details).

The default viewport shows only `DefaultLayers::DefaultLayer`


## Multi viewport

Additional viewports can be created by calling
```c++
ui::Entity camera_entity = add_camera(ui::Registry &, ui::Camera camera);
// or use get_focused_camera_entity(ui::Registry &)  to reuse current camera

// Creates an offscreen viewport with the specified camera
ui::Entity viewport_entity = add_viewport(ui::Registry &, ui::Entity camera_entity)

// Creates a UI panel that shows the viewport
ui::Entity viewport_entity = add_viewport_panel(ui::Registry &, const std::string & name, ui::Entity viewport_entity);
```
