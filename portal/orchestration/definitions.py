"""Dagster definitions: a thin layer over `portal.pipeline.stages` (ТЗ 5.5).

Run the UI with `dagster dev -m portal.orchestration.definitions`. The pipeline itself
does not depend on Dagster and runs without it: `python -m portal.pipeline run`.
"""

import json
import os
import urllib.request

from dagster import (
    AssetCheckResult,
    AssetCheckSpec,
    AssetExecutionContext,
    AutomationCondition,
    Backoff,
    Definitions,
    MaterializeResult,
    RetryPolicy,
    RunFailureSensorContext,
    RunRequest,
    StaticPartitionsDefinition,
    asset,
    define_asset_job,
    run_failure_sensor,
    schedule,
)

from portal.pipeline import stages
from portal.settings import build_dir, db_path, get_source, load_sources

SOURCES = load_sources()
# Each registered source is a partition (ТЗ 5.5, item 3): the registry, not this file, lists them.
source_partitions = StaticPartitionsDefinition([source.id for source in SOURCES])
# Retries with exponential delay (ТЗ 5.5, item 4).
retry = RetryPolicy(max_retries=3, delay=30, backoff=Backoff.EXPONENTIAL)


@asset(partitions_def=source_partitions, retry_policy=retry, group_name="aggregation", pool="sources")
def source_snapshot(context: AssetExecutionContext) -> MaterializeResult:
    """Stage 1: immutable, content-addressed snapshot of the source dump."""
    snapshot = stages.collect(get_source(context.partition_key), build_dir())
    return MaterializeResult(metadata={
        "rows": snapshot["rows"],
        "candidate_rows": snapshot["candidate_rows"] or 0,
        "sha256": snapshot["sha256"],
        "collected_at": snapshot["collected_at"],
    })


@asset(partitions_def=source_partitions, deps=[source_snapshot], retry_policy=retry, group_name="aggregation")
def normalized_records(context: AssetExecutionContext) -> MaterializeResult:
    """Stages 2–6: mapping, normalization, relevance, entity links and quality tiers."""
    result = stages.transform(get_source(context.partition_key), build_dir())
    return MaterializeResult(metadata={
        "input": result["input"],
        "output": result["output"],
        "rules_version": result["rules_version"],
        "date_methods": json.dumps(result["date_methods"]),
        "media_types": json.dumps(result["media_types"]),
        "seconds": result["seconds"],
    })


@asset(
    deps=[normalized_records],
    group_name="publication",
    check_specs=[AssetCheckSpec(name="record_volume", asset="search_index", blocking=True)],
    automation_condition=AutomationCondition.eager(),
)
def search_index() -> MaterializeResult:
    """Stage 8: record store, full-text index, facets, entities and bulk dumps.

    `stages.publish` raises before replacing the live index when a critical check
    fails (ТЗ 5.5, item 7), so the run fails and the previous publication stays.
    """
    report = stages.publish(SOURCES, build_dir(), db_path())
    return MaterializeResult(
        metadata={
            "records": report["published"]["records"],
            "with_media": report["published"]["with_media"],
            "institutions": report["published"]["institutions"],
            "entities": report["published"]["entities"],
            "database_bytes": report["database"]["bytes"],
        },
        check_results=[
            AssetCheckResult(
                check_name="record_volume",
                passed=all(check["passed"] for check in report["checks"]),
                metadata={check["source"]: check["detail"] for check in report["checks"]},
            )
        ],
    )


aggregation_job = define_asset_job(
    "aggregate_source", selection=[source_snapshot, normalized_records], partitions_def=source_partitions
)


def _source_schedule(source):
    @schedule(cron_schedule=source.schedule, job=aggregation_job, name=f"{source.id}_schedule")
    def _schedule():
        return RunRequest(partition_key=source.id)

    return _schedule


@run_failure_sensor(name="notify_curators")
def notify_curators(context: RunFailureSensorContext):
    """Failure alerts (ТЗ 5.5, item 9): posted to a webhook when PORTAL_ALERT_WEBHOOK is set."""
    message = f"Pipeline run {context.dagster_run.run_id} ({context.dagster_run.job_name}) failed: " \
              f"{context.failure_event.message}"
    context.log.error(message)
    webhook = os.environ.get("PORTAL_ALERT_WEBHOOK")
    if webhook:
        request = urllib.request.Request(
            webhook, data=json.dumps({"text": message}).encode(), headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(request, timeout=10)


defs = Definitions(
    assets=[source_snapshot, normalized_records, search_index],
    jobs=[aggregation_job],
    schedules=[_source_schedule(source) for source in SOURCES if source.schedule],
    sensors=[notify_curators],
)
