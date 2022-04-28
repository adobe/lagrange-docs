<!-- $ignore -->

# Lights

## Image Based Lighting

Refer to `ui/utils/ibl.h` for all IBL utility functions and `ui/components/IBL.h` for the IBL component.

### Loading/Generating IBL

```c++
//From disk file
ui::IBL ibl = ui::generate_ibl("path.hdr");
//From texture
std::shared_ptr<ui::Texture> texture;
ui::IBL ibl = ui::generate_ibl(texture);
```

### Adding IBL to scene

```c++
ui::IBL ibl = ...;
Entity ibl_entity = ui::add_ibl(registry, ibl);
```


### Changing IBL options
```c++
//Get IBL (if there are multiple, the first one is returned)
ui::IBL &ibl = *ui::get_ibl(registry);

// Blur the IBL (number corresponds to mip map level)
ibl.blur = 2.0f;

// Disable rendering of the IBL image in the background
// The IBL is still used for shading objects.
ibl.show_skybox = false;
```



## Analytic Lights

Refer to `ui/utils/lights.h` for all light utility functions and `ui/components/Light.h.` for the Light component:

```c++
// Omni-directional point light source
Entity point_light = add_point_light(registry, intensity, position);

// Directional light source at infinite distance
Entity point_light = add_directional_light(registry, intensity, direction);

// Light in a cone
Entity spot_lighj = add_spot_light(registry, intensity, position, direction, cone_angle_radians);
```
