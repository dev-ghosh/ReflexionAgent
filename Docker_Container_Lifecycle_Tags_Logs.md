# Docker: Container Lifecycle, Image Tags & Versioning, and Container Logs

## 1. Docker Container Lifecycle

A Docker container goes through different states during its lifetime.

### Basic Lifecycle

``` text
Image
  ↓
docker create
  ↓
Created
  ↓
docker start
  ↓
Running
  ↓
docker stop
  ↓
Stopped
  ↓
docker start
  ↓
Running
  ↓
docker rm
  ↓
Removed
```

### `docker create`

Creates a container from an image but does **not** start it.

``` bash
docker create nginx
```

### `docker start`

Starts an already-created container.

``` bash
docker start <container_id>
```

### `docker run`

`docker run` creates and starts a new container.

``` bash
docker run nginx
```

Conceptually:

``` text
docker run = docker create + docker start
```

### `docker stop`

Stops a running container. The container still exists.

``` bash
docker stop <container_id>
```

### `docker restart`

Restarts an existing container.

``` bash
docker restart <container_id>
```

### `docker rm`

Removes a stopped container.

``` bash
docker rm <container_id>
```

> Stopping a container does not delete it. Removing a container does not
> automatically remove its image.

------------------------------------------------------------------------

# 2. Docker Image Tags and Versioning

A Docker image normally has a name and a tag.

Example:

``` bash
nginx:1.27
```

Here:

``` text
nginx  → Image name
1.27   → Tag
```

Other examples:

``` text
nginx:latest
nginx:1.27.1
python:3.11
python:3.11-slim
node:22-alpine
```

## Why Tags Matter

A tag can identify a particular version or variant of an image.

For example:

``` bash
docker pull python:3.11
```

is more predictable than relying on:

``` bash
docker pull python:latest
```

The `latest` tag is simply a tag name; it does not inherently mean "most
recent stable version" in every context.

## Versioning Best Practice

For production applications, prefer a known image version or an image
digest rather than relying blindly on `latest`.

Example:

``` bash
docker pull nginx:1.27.1
```

This helps make deployments more reproducible.

------------------------------------------------------------------------

# 3. Container Logs

Containerized applications commonly write output to `stdout` and
`stderr`. Docker can collect this output as container logs.

## View Logs

``` bash
docker logs <container_id>
```

or:

``` bash
docker logs <container_name>
```

Example:

``` bash
docker run --name my-nginx nginx
docker logs my-nginx
```

## Follow Logs in Real Time

``` bash
docker logs -f my-nginx
```

Press `Ctrl + C` to stop following the logs.

## Show Recent Logs

``` bash
docker logs --tail 50 my-nginx
```

## Show Logs with Timestamps

``` bash
docker logs -t my-nginx
```

## Combine Options

``` bash
docker logs -f --tail 100 -t my-nginx
```

------------------------------------------------------------------------

# 4. Why Container Logs Are Important

Logs help developers:

-   Debug applications
-   Find errors
-   Monitor application behavior
-   Investigate crashes
-   Understand what happened inside a container

Basic flow:

``` text
Application
    ↓
stdout / stderr
    ↓
Docker logging
    ↓
docker logs
    ↓
Developer
```

------------------------------------------------------------------------

# 5. Important Docker Commands

  Command                 Purpose
  ----------------------- -----------------------------
  `docker create nginx`   Create a container
  `docker start <id>`     Start an existing container
  `docker run nginx`      Create + start a container
  `docker stop <id>`      Stop a container
  `docker restart <id>`   Restart a container
  `docker rm <id>`        Remove a container
  `docker ps`             Show running containers
  `docker ps -a`          Show all containers
  `docker logs <id>`      Show container logs
  `docker logs -f <id>`   Follow logs
  `docker images`         Show local images

------------------------------------------------------------------------

# Key Takeaways

-   A **container** is an instance created from a Docker image.
-   `docker run` creates and starts a new container.
-   `docker create` only creates the container.
-   `docker start` starts an existing container.
-   `docker stop` stops a container without removing it.
-   `docker rm` removes a container.
-   An image **tag** identifies a version or variant, such as
    `nginx:1.27`.
-   Explicit image versions make deployments more predictable.
-   `docker logs` lets you inspect container output.
-   `docker logs -f` follows logs in real time.
