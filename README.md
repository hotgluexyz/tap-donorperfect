# tap-donorperfect

`tap-donorperfect` is a Singer tap for DonorPerfect.

## Installation

```bash
pipx install tap-donorperfect
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-donorperfect --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `tap-donorperfect` by itself or in a pipeline.

### Executing the Tap Directly

```bash
tap-donorperfect --version
tap-donorperfect --help
tap-donorperfect --config CONFIG --discover > ./catalog.json
```

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_donorperfect/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-donorperfect` CLI interface directly using `poetry run`:

```bash
poetry run tap-donorperfect --help
```

## Streams

- `donors`
- `flags`
- `donor_addresses`
