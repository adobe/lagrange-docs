# Lagrange

{% if is_corp %}
{% include 'corp/badges.md' %}
{% endif %}

Project Lagrange is an initiative to bring the power of robust geometry
processing to Adobe products. It bridges cutting edge research works with
cutting edge products. Project Lagrange is built on the following design
principles:

{% if is_corp %}

![](open/img/intro.png){ width=600 }

{% endif %}

## Modular Design

Large features should be decomposed into smaller _single functionality_ modules
that are _as decoupled as possible_ from each other.  Modular design enables
unit testing, prevents small change from propagating widely in the code base,
and makes adding new functionalities easy.

## Preconditions + Guarantees

Algorithmic correctness should be rigorously enforced.  This is achieved by
clearly documenting and checking the precise precondition and the corresponding
guarantees of each module.  Algorithms relying on input-dependent parameter
tuning should be avoided.

## Interface + Compute Engine

The interface of a functionality should be decoupled from the computation
algorithms.  This makes swapping out an algorithm with a better algorithm
possible and ideally should not require change in client codes.

## Large Scale Testing

Large scale, empirical testing on major functionalities should be carried out
periodically to ensure their correctness and robustness.  Let data speak for
itself.
