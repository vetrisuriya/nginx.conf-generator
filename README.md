# Nginx Config Studio

A web-based tool for creating production-ready Nginx configuration files with live preview and one-click download.

## Overview

Nginx Config Studio is an interactive web application that allows you to generate `nginx.conf` files through a user-friendly interface. Configure your server settings, add location blocks, and see the configuration update in real-time.

## Features

- **Live Preview**: See your Nginx configuration update instantly as you make changes
- **Interactive Controls**: Easy-to-use form inputs for all major Nginx directives
- **Location Block Management**: Add, remove, and reorder location blocks with automatic precedence sorting
- **One-Click Download**: Export your generated configuration file directly to your computer
- **Responsive Design**: Works on desktop and mobile devices
- **Default Configurations**: Pre-loaded with sensible defaults for quick setup

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)
- No server or installation required - runs entirely in the browser

### Usage

1. **Open the Application**: Open `index.html` in your web browser
2. **Configure Global Settings**:
   - Server name (domain)
   - Root directory path
   - Listen port
   - Default MIME type
   - Error and access log paths
3. **Add Routing Features**:
   - Rewrite rules
   - Redirects
   - Try files directives
4. **Manage Location Blocks**:
   - Add location patterns with different modifiers (=, ^~, ~, ~*)
   - Specify directives for each location
   - Locations are automatically sorted by Nginx precedence
5. **Preview and Download**:
   - Watch the live preview update as you type
   - Click "Download nginx.conf" to save your configuration

## Configuration Options

### Global Settings

- **Server Name**: Domain name(s) for the server block
- **Root Directory**: Base directory for serving files
- **Listen Port**: Port number for Nginx to listen on
- **Default Type**: Default MIME type for unknown file types
- **Error Log**: Path and log level for error logging
- **Access Log**: Path and format for access logging

### Routing Features

- **Rewrite Rule**: URL rewriting using Nginx rewrite syntax
- **Redirect**: HTTP redirects (301, 302, etc.)
- **Try Files**: Fallback file serving order

### Location Blocks

Location blocks support all Nginx location modifiers:

- **Prefix Match** (no modifier): Standard prefix matching
- **Exact Match** (`=`): Exact URI match
- **Preferential Prefix** (`^~`): Prefix match that takes precedence over regex
- **Case-Sensitive Regex** (`~`): Regular expression matching
- **Case-Insensitive Regex** (`~*`): Case-insensitive regex matching

Each location can have multiple directives separated by `|`.

## Default Configuration

The application comes pre-loaded with example configurations including:

- Health check endpoint (`/healthz`)
- Static asset caching (`/assets/`)
- Image file caching (PNG, JPG, JPEG, GIF, ICO)
- Backend proxy pass with upstream configuration
- Named location for app routing

## Contributing

1. Fork the repository
2. Make your changes to the HTML, CSS, or JavaScript files
3. Test in multiple browsers
4. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions, please open a GitHub issue in this repository.