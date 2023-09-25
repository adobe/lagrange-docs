# Getting Started

{% if is_corp %}
{% include 'corp/setup.md' %}
{% endif %}

## Compiling Lagrange

- How to [compile Lagrange](build.md).
- How to [run unit tests](dev/unit-tests.md).
{% if is_corp %}
- Example project templates using Lagrange:
    - [C++ Project]({{ cpp_project_url }})
    - [Python Project]({{ python_project_url }})
    - [C++/Python Bindings]({{ binding_project_url }})
{% else %}
- [Example project template]({{ cpp_project_url }}) using Lagrange.
{% endif %}

## Contributing

- Read our [contributing page](dev/contribute.md).
- Read our [code style guide](dev/code-style.md).
{% if is_corp %}
- How to upload new test data to [Artifactory](../corp/dev/artifactory.md).
{% endif %}
