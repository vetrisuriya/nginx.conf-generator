const defaultLocations = [
  { modifier: '=', pattern: '/healthz', directives: "return 200 'ok'" },
  { modifier: '^~', pattern: '/assets/', directives: "expires 1y | add_header Cache-Control 'public, immutable'" },
  { modifier: '~*', pattern: '\\.(png|jpg|jpeg|gif|ico)$', directives: 'expires 30d' },
  { modifier: '', pattern: '/', directives: 'proxy_pass http://app_backend | proxy_set_header Host $host' },
  { modifier: '', pattern: '@app', directives: 'proxy_pass http://app_backend' }
];

const locationsRoot = document.getElementById('locations');
const template = document.getElementById('locationTemplate');
const preview = document.getElementById('preview');

function addLocation(data = { modifier: '', pattern: '/', directives: 'return 200' }) {
  const node = template.content.firstElementChild.cloneNode(true);
  node.querySelector('[data-field="modifier"]').value = data.modifier;
  node.querySelector('[data-field="pattern"]').value = data.pattern;
  node.querySelector('[data-field="directives"]').value = data.directives;
  node.querySelector('[data-action="remove"]').addEventListener('click', () => {
    node.remove();
    render();
  });

  node.querySelectorAll('input,select').forEach(el => el.addEventListener('input', render));
  locationsRoot.appendChild(node);
}

function precedence(modifier) {
  if (modifier === '=') return 0;
  if (modifier === '^~') return 1;
  if (modifier === '~' || modifier === '~*') return 2;
  return 3;
}

function buildConfig() {
  const listen = document.getElementById('listen').value || '80';
  const serverName = document.getElementById('serverName').value || '_';
  const root = document.getElementById('root').value.trim();
  const defaultType = document.getElementById('defaultType').value.trim() || 'application/octet-stream';
  const errorLog = document.getElementById('errorLog').value.trim();
  const accessLog = document.getElementById('accessLog').value.trim();
  const rewrite = document.getElementById('rewrite').value.trim();
  const redirect = document.getElementById('redirect').value.trim();
  const tryFiles = document.getElementById('tryFiles').value.trim();

  const locationRows = [...locationsRoot.querySelectorAll('.location-row')].map((row) => {
    const modifier = row.querySelector('[data-field="modifier"]').value;
    const pattern = row.querySelector('[data-field="pattern"]').value.trim();
    const directives = row.querySelector('[data-field="directives"]').value
      .split('|')
      .map(d => d.trim())
      .filter(Boolean);
    return { modifier, pattern, directives };
  }).filter(l => l.pattern);

  locationRows.sort((a, b) => {
    const p = precedence(a.modifier) - precedence(b.modifier);
    if (p !== 0) return p;
    return b.pattern.length - a.pattern.length;
  });

  const lines = [
    'worker_processes auto;',
    '',
    'events {',
    '    worker_connections 1024;',
    '}',
    '',
    'http {',
    '    include /etc/nginx/mime.types;',
    `    default_type ${defaultType};`,
    '',
    '    upstream app_backend {',
    '        least_conn;',
    '        server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;',
    '        server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;',
    '    }',
    '',
    '    server {',
    `        listen ${listen};`,
    `        server_name ${serverName};`,
  ];

  if (root) lines.push(`        root ${root};`);
  lines.push('        index index.html index.htm;');
  if (errorLog) lines.push(`        error_log ${errorLog};`);
  if (accessLog) lines.push(`        access_log ${accessLog};`);
  if (rewrite) lines.push(`        rewrite ${rewrite};`);
  if (redirect) lines.push(`        return ${redirect};`);
  if (tryFiles) lines.push(`        try_files ${tryFiles};`);

  for (const loc of locationRows) {
    lines.push('');
    const modifier = loc.modifier ? `${loc.modifier} ` : '';
    lines.push(`        location ${modifier}${loc.pattern} {`);
    loc.directives.forEach(d => lines.push(`            ${d.replace(/;$/, '')};`));
    lines.push('        }');
  }

  lines.push('    }', '}');
  return lines.join('\n') + '\n';
}

function render() {
  preview.textContent = buildConfig();
}

document.getElementById('addLocationBtn').addEventListener('click', () => {
  addLocation();
  render();
});

document.querySelectorAll('input,select').forEach(el => el.addEventListener('input', render));

document.getElementById('downloadBtn').addEventListener('click', () => {
  const blob = new Blob([buildConfig()], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'nginx.conf';
  a.click();
  URL.revokeObjectURL(a.href);
});

document.getElementById('resetBtn').addEventListener('click', () => {
  document.getElementById('serverName').value = 'example.com www.example.com';
  document.getElementById('root').value = '/var/www/example';
  document.getElementById('listen').value = '80';
  document.getElementById('defaultType').value = 'application/octet-stream';
  document.getElementById('errorLog').value = '/var/log/nginx/example.error.log warn';
  document.getElementById('accessLog').value = '/var/log/nginx/example.access.log main';
  document.getElementById('rewrite').value = '^/old/(.*)$ /new/$1 permanent';
  document.getElementById('redirect').value = '301 https://$host$request_uri';
  document.getElementById('tryFiles').value = '$uri $uri/ @app';
  locationsRoot.innerHTML = '';
  defaultLocations.forEach(addLocation);
  render();
});

defaultLocations.forEach(addLocation);
render();
