# Getting Started

{% if is_corp %}
{% include 'corp/setup.md' %}
{% endif %}

## Compiling Lagrange

- How to [compile Lagrange](build.md).
- How to [run unit tests](dev/unit-tests.md).
- [Example project template]({{ example_project_url }}) using Lagrange.

## Contributing

- Read our [contributing page](dev/contribute.md).
- Read our [code style guide](dev/code-style.md).
{% if is_corp %}
- How to upload new test data to [Artifactory](../corp/dev/artifactory.md).
{% endif %}
