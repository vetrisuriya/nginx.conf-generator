from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass
class Location:
    pattern: str
    modifier: str = ""
    directives: list[str] = field(default_factory=list)

    def render(self, indent: int = 1) -> str:
        pad = "    " * indent
        header = f"{pad}location {self.modifier + ' ' if self.modifier else ''}{self.pattern} {{".rstrip()
        lines = [header]
        for directive in self.directives:
            lines.append(f"{pad}    {directive.rstrip(';')};")
        lines.append(f"{pad}}}")
        return "\n".join(lines)


@dataclass
class ServerBlock:
    listen: list[int] = field(default_factory=lambda: [80])
    server_name: str = "_"
    root: str | None = None
    index: list[str] = field(default_factory=lambda: ["index.html"])
    error_log: str | None = None
    access_log: str | None = None
    rewrites: list[str] = field(default_factory=list)
    redirects: list[str] = field(default_factory=list)
    try_files: str | None = None
    locations: list[Location] = field(default_factory=list)
    extra_directives: list[str] = field(default_factory=list)

    def render(self, indent: int = 1) -> str:
        pad = "    " * indent
        lines = [f"{pad}server {{"]
        for port in self.listen:
            lines.append(f"{pad}    listen {port};")
        lines.append(f"{pad}    server_name {self.server_name};")
        if self.root:
            lines.append(f"{pad}    root {self.root};")
        if self.index:
            lines.append(f"{pad}    index {' '.join(self.index)};")
        if self.error_log:
            lines.append(f"{pad}    error_log {self.error_log};")
        if self.access_log:
            lines.append(f"{pad}    access_log {self.access_log};")

        for rw in self.rewrites:
            lines.append(f"{pad}    rewrite {rw.rstrip(';')};")
        for rd in self.redirects:
            lines.append(f"{pad}    return {rd.rstrip(';')};")

        if self.try_files:
            lines.append(f"{pad}    try_files {self.try_files.rstrip(';')};")

        for directive in self.extra_directives:
            lines.append(f"{pad}    {directive.rstrip(';')};")

        for location in sorted(self.locations, key=location_precedence_key):
            lines.append("")
            lines.append(location.render(indent=indent + 1))

        lines.append(f"{pad}}}")
        return "\n".join(lines)


def location_precedence_key(location: Location) -> tuple[int, int]:
    """
    Sort by nginx matching precedence:
    exact (=) > preferential prefix (^~) > regex (~, ~*) > prefix (none)
    """
    precedence_map = {
        "=": 0,
        "^~": 1,
        "~": 2,
        "~*": 2,
        "": 3,
    }
    return precedence_map.get(location.modifier, 4), -len(location.pattern)


@dataclass
class NginxSpec:
    mime_types_include: str = "/etc/nginx/mime.types"
    default_type: str = "application/octet-stream"
    include_files: list[str] = field(default_factory=list)
    env_variables: dict[str, str] = field(default_factory=dict)
    upstreams: list[dict[str, Any]] = field(default_factory=list)
    maps: list[str] = field(default_factory=list)
    http_directives: list[str] = field(default_factory=list)
    servers: list[ServerBlock] = field(default_factory=list)

    def render(self) -> str:
        lines = ["worker_processes auto;", ""]

        for name, value in self.env_variables.items():
            lines.append(f"env {name}={value};")

        lines.extend([
            "events {",
            "    worker_connections 1024;",
            "}",
            "",
            "http {",
            f"    include {self.mime_types_include};",
            f"    default_type {self.default_type};",
            "",
        ])

        for path in self.include_files:
            lines.append(f"    include {path};")

        if self.include_files:
            lines.append("")

        for m in self.maps:
            lines.append(f"    map {m.rstrip(';')};")

        if self.maps:
            lines.append("")

        for upstream in self.upstreams:
            lines.extend(render_upstream(upstream, indent=1))
            lines.append("")

        for directive in self.http_directives:
            lines.append(f"    {directive.rstrip(';')};")

        if self.http_directives:
            lines.append("")

        for server in self.servers:
            lines.append(server.render(indent=1))
            lines.append("")

        if lines[-1] == "":
            lines.pop()
        lines.append("}")
        return "\n".join(lines)


def render_upstream(upstream: dict[str, Any], indent: int = 1) -> list[str]:
    pad = "    " * indent
    name = upstream.get("name", "backend")
    lines = [f"{pad}upstream {name} {{"]
    for server in upstream.get("servers", []):
        lines.append(f"{pad}    server {server.rstrip(';')};")
    for directive in upstream.get("directives", []):
        lines.append(f"{pad}    {directive.rstrip(';')};")
    lines.append(f"{pad}}}")
    return lines


def from_dict(data: dict[str, Any]) -> NginxSpec:
    servers = []
    for raw_server in data.get("servers", []):
        locations = [
            Location(
                pattern=raw_location["pattern"],
                modifier=raw_location.get("modifier", ""),
                directives=raw_location.get("directives", []),
            )
            for raw_location in raw_server.get("locations", [])
        ]
        servers.append(
            ServerBlock(
                listen=raw_server.get("listen", [80]),
                server_name=raw_server.get("server_name", "_"),
                root=raw_server.get("root"),
                index=raw_server.get("index", ["index.html"]),
                error_log=raw_server.get("error_log"),
                access_log=raw_server.get("access_log"),
                rewrites=raw_server.get("rewrites", []),
                redirects=raw_server.get("redirects", []),
                try_files=raw_server.get("try_files"),
                locations=locations,
                extra_directives=raw_server.get("extra_directives", []),
            )
        )

    return NginxSpec(
        mime_types_include=data.get("mime_types_include", "/etc/nginx/mime.types"),
        default_type=data.get("default_type", "application/octet-stream"),
        include_files=data.get("include_files", []),
        env_variables=data.get("env_variables", {}),
        upstreams=data.get("upstreams", []),
        maps=data.get("maps", []),
        http_directives=data.get("http_directives", []),
        servers=servers,
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate nginx.conf from a JSON spec")
    parser.add_argument("--input", "-i", required=True, help="Path to JSON specification")
    parser.add_argument("--output", "-o", help="Output file path (defaults to stdout)")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    with open(args.input, "r", encoding="utf-8") as infile:
        spec = from_dict(json.load(infile))
    content = spec.render() + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8") as outfile:
            outfile.write(content)
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
