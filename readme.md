# Crossmint

This project is a Python-based tool for creating patterns in the Megaverse using Crossmint’s API. The script leverages the Megaverse API to automate the placement of Polyanets in an X-shaped pattern in Phase 1, as well as other astral objects like Soloons and Comeths in Phase 2.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- **Python 3.7+**
- **Pip** (Python package manager)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/shrey/crossmint.git
   cd crossmint
   ```

2. **Install Dependencies**
   Install the required packages using pip:

   ```bash
   pip install requests
   ```

## Configuration

The project requires configuration via environment variables. Set up these variables in your terminal session or within a `.env` file (if using a tool like `python-dotenv` to load the environment file).

### Environment Variables

- **API_BASE_URL**: The base URL of the Megaverse API (default: `https://challenge.crossmint.io/api`).
- **CANDIDATE_ID**: Your unique candidate ID provided by Crossmint.

#### Example

To set these environment variables temporarily for your terminal session:

```bash
export API_BASE_URL="https://challenge.crossmint.io/api"
export CANDIDATE_ID="your_candidate_id_here"
```

Alternatively, create a `.env` file with the following content:

```plaintext
API_BASE_URL=https://challenge.crossmint.io/api
CANDIDATE_ID=your_candidate_id_here
```

## Usage

Run the `Crossmint` by executing the `phase_one.py` and `phase_two.py` script:

```bash
python phase_one.py
python phase_two.py
```

This will:

1. Retrieve the goal map (if applicable).
2. Generate an X-shaped pattern in the Megaverse or execute other object placements as defined in the goal map.
3. Log the creation status for each astral object.

### Example Output

```plaintext
INFO:__main__:Starting X-shape creation...
INFO:__main__:Successfully created Polyanet at Position(row=2, column=2)
INFO:__main__:Successfully created Polyanet at Position(row=2, column=8)
...
INFO:__main__:X-shape creation completed!
```

## Troubleshooting

- **Environment Variable Errors**:

  - Ensure that `CANDIDATE_ID` is set in your environment. If it's missing, the program will log an error and exit.

- **Network Issues**:

  - If API requests fail due to network issues, the script will automatically retry up to 3 times with exponential backoff.

- **Rate Limiting**:

  - The script includes a delay between API calls to prevent rate limiting. You may increase the delay if encountering issues.

- **API Errors**:

  - If the API returns errors, check the provided `candidateId` and base URL for accuracy.
