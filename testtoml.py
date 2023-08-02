#!/usr/bin/env python


import toml

with open('test.toml', 'r') as f:
   config = toml.load(f)

print(config)


