"""Command-line entry point: `python -m portal.pipeline run`."""

import argparse
import json
import sys

from portal.pipeline import stages
from portal.settings import build_dir, db_path, get_source, load_sources


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m portal.pipeline", description=__doc__)
    parser.add_argument("stage", choices=["collect", "transform", "publish", "run"])
    parser.add_argument("--source", action="append", help="Source id from config/sources.toml; repeatable")
    parser.add_argument("--force", action="store_true", help="Publish even if a critical quality check fails")
    parser.add_argument("--no-export", action="store_true", help="Skip JSON Lines and Parquet dumps")
    args = parser.parse_args(argv)

    sources = [get_source(source_id) for source_id in args.source] if args.source else load_sources()
    build, db = build_dir(), db_path()
    result = {}
    entities = None
    if args.stage in ("collect", "run"):
        result["collect"] = [stages.collect(source, build) for source in sources]
    if args.stage in ("transform", "run"):
        entities = stages.entity_dictionary()
        result["transform"] = [stages.transform(source, build, entities) for source in sources]
    if args.stage in ("publish", "run"):
        # Publication always covers every registered source, so one source cannot hide the others.
        try:
            result["publish"] = stages.publish(
                load_sources(), build, db, entities, force=args.force, with_export=not args.no_export
            )
        except stages.QualityGateError as error:
            print(f"Publication blocked by a quality check: {error}", file=sys.stderr)
            return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
