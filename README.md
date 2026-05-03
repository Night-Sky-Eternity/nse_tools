```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Update nse_pytoolkit vendor",
            "type": "shell",
            "command": "tmpdir=$(mktemp -d) && git clone --depth 1 https://github.com/Night-Sky-Eternity/nse_pytoolkit.git \"$tmpdir\" && rm -rf src/arc_garden/nse_pytoolkit && cp -r \"$tmpdir/src/nse_pytoolkit\" src/arc_garden/nse_pytoolkit && rm -rf \"$tmpdir\" && echo 'Done.'",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared"
            },
            "problemMatcher": []
        }
    ]
}

```