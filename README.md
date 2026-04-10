This repository is part of a system for technical analysis of a Polymarket NBA data. You can learn more [here](https://sonyn.dev/blog/2026-04-07-a-random-walk-down-diamond-district/).

Report service creates reports on Polymarket NBA-related event statistics provided by [Polymarket NBA Oracle](https://github.com/etchedheadplate/polymarket-nba-oracle).

## Examples

### Quote Series

Token quotes change history during a specific game with local price minima during underdog segments.

![quote_series_report](media/quote_series_report.jpg)

### Price Window

History of a team entering a specific price window in a game versus a specified team or all teams.

![price_window_report](media/price_window_report.jpg)

## Usage

### Enviroment

Create a `.env` file in the root of the repository using the `.env.example` template.

To run this service, the [Polymarket NBA Oracle](https://github.com/etchedheadplate/polymarket-nba-oracle) database must be deployed first.

Background images and font files are not included in this repository. The service will fall back to a black background and the system default font if these files are not provided.

### Running

The system is built around a RabbitMQ-based task processing model. A consumer subscribes to task queues, executes incoming tasks, and publishes results back to response queues.

Start RabbitMQ consumer:

```bash
python -m main
```
