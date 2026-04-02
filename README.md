This service creates visual reports on Polymarket NBA-related event statistics. The system is built around a RabbitMQ-based task processing model. A consumer subscribes to task queues, executes incoming tasks, and publishes results back to response queues.

The service can be adapted for processing game events from other sports leagues (e.g. WNBA, NHL, NFL).

## Examples

![quote_series_report](media/quote_series_report.jpg)

![price_window_rreport](media/price_window_rreport.jpg)


## Usage

Start RabbitMQ consumer:

```bash
python -m main
```
