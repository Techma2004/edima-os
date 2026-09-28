# Edima OS Installation

Edima separates installation profiles from hardware profiles.

## Installation profiles

- minimal — smallest usable Edima desktop
- standard — normal Edima workstation
- developer — full developer and networking toolkit
- everything — every Edima-managed package

## Hardware profiles

Hardware profiles do not restrict installation.

For example:

    Hardware:     low-resource
    Installation: everything

is valid.

Hardware profiles control runtime behaviour such as background services,
indexing, animations, and automatic startup.

Installation profiles control what software is installed.

This separation is intentional.
