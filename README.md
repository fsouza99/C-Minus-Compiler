# C-Minus-Compiler

A compiler project for the C-Minus language implemented in Python.
For now, it contains a scanner and a parser.

## Directories

The *examples* directory contains code files written in C-Minus. The *(error)* variants are these same *.cm* files, by with selected errors included for testing purposes.

The scanner produces the *.trace* files. They contain the tokens extracted through complete *.cm* file readings.

The parser produces the *.tree* files, which hold the syntax tree of a program in a *.cm* file.