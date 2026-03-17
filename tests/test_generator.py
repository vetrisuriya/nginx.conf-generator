from nginx_conf_generator import Location, ServerBlock, from_dict, location_precedence_key


def test_location_precedence_order():
    locations = [
        Location(pattern="/", modifier=""),
        Location(pattern="/exact", modifier="="),
        Location(pattern="/static/", modifier="^~"),
        Location(pattern="\\.php$", modifier="~"),
    ]

    sorted_locations = sorted(locations, key=location_precedence_key)
    assert [l.modifier for l in sorted_locations] == ["=", "^~", "~", ""]


def test_generate_config_sections_present():
    spec = from_dict(
        {
            "env_variables": {"APP_ENV": "production"},
            "upstreams": [{"name": "backend", "servers": ["127.0.0.1:8080"]}],
            "servers": [
                {
                    "server_name": "example.com",
                    "locations": [{"pattern": "/", "directives": ["return 200"]}],
                    "error_log": "/var/log/nginx/error.log",
                    "access_log": "/var/log/nginx/access.log",
                }
            ],
        }
    )

    content = spec.render()
    assert "include /etc/nginx/mime.types;" in content
    assert "upstream backend" in content
    assert "error_log /var/log/nginx/error.log;" in content
    assert "access_log /var/log/nginx/access.log;" in content
    assert "location / {" in content
