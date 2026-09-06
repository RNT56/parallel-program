# Manifests

Changes to single-writer resources that every lane touches (a string catalog, a lockfile, a
generated index, a registry) are not edited by lanes. A lane writes a manifest here as
`<lane-key>.md` in the shape below; {{INTEGRATOR}} applies every manifest once per checkpoint, each
as its own commit, and posts the SHA on the board.

```
## <resource path>

### REMOVED
- <key or entry>

### ADDED
- <key or entry>: <value>

### CHANGED
- <key or entry>: <old> -> <new>
```
