#!/usr/bin/env python3
"""Query the superconductor database.

Usage:
    python scripts/query_database.py                     # list all
    python scripts/query_database.py --tc-min 100        # Tc >= 100 K
    python scripts/query_database.py --tc-max 50         # Tc <= 50 K
    python scripts/query_database.py --pressure 0       # ambient pressure
    python scripts/query_database.py --name "MgB2"       # exact name match
    python scripts/query_database.py --composition "H3S"  # composition filter
    python scripts/query_database.py --synthesis-method "HPHT"  # synthesis method filter
    python scripts/query_database.py --tc-min 30 --tc-max 100 --pressure 0
    python scripts/query_database.py --output json       # output as JSON
    python scripts/query_database.py --output csv        # output as CSV
    python scripts/query_database.py --output table      # output as table (default)
    python scripts/query_database.py --external-db materials_project --api-key YOUR_KEY
"""

import json
import argparse
import sys
import os
import urllib.request
import urllib.parse

DATABASE_PATH = "data/superconductor_database.json"

def load_database(path):
    with open(path, "r") as f:
        return json.load(f)

def query(entries, args):
    results = []
    for entry in entries:
        if args.name and entry.get("name", "") != args.name:
            continue
        if args.tc_min is not None and entry.get("Tc", 0) < args.tc_min:
            continue
        if args.tc_max is not None and entry.get("Tc", 0) > args.tc_max:
            continue
        if args.pressure is not None and entry.get("pressure", 0) != args.pressure:
            continue
        if args.pressure_min is not None and entry.get("pressure", 0) < args.pressure_min:
            continue
        if args.pressure_max is not None and entry.get("pressure", 0) > args.pressure_max:
            continue
        if args.composition and entry.get("composition") != args.composition:
            continue
        if args.synthesis and entry.get("synthesis") != args.synthesis:
            continue
        if args.synthesis_method and entry.get("synthesis_method") != args.synthesis_method:
            continue
        if args.mechanism and entry.get("mechanism") != args.mechanism:
            continue
        results.append(entry)
    return results

def query_external_database(db_name, params, api_key=None):
    """Query an external database and return list of entries."""
    if db_name == "materials_project":
        if not api_key:
            print("Error: Materials Project API key required. Set MATERIALS_API_KEY environment variable or use --api-key.", file=sys.stderr)
            sys.exit(1)
        base_url = "https://api.materialsproject.org/materials"
        query_params = {}
        if params.get("name"):
            query_params["material_ids"] = params["name"]
        if params.get("composition"):
            query_params["formula"] = params["composition"]
        if params.get("tc_min") is not None:
            query_params["tc_min"] = params["tc_min"]
        if params.get("tc_max") is not None:
            query_params["tc_max"] = params["tc_max"]
        if params.get("pressure") is not None:
            query_params["pressure"] = params["pressure"]
        if params.get("pressure_min") is not None:
            query_params["pressure_min"] = params["pressure_min"]
        if params.get("pressure_max") is not None:
            query_params["pressure_max"] = params["pressure_max"]
        if params.get("synthesis_method"):
            query_params["synthesis_method"] = params["synthesis_method"]
        if params.get("mechanism"):
            query_params["mechanism"] = params["mechanism"]
        query_params["api_key"] = api_key
        url = base_url + "?" + urllib.parse.urlencode(query_params)
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                entries = data.get("data", [])
                results = []
                for item in entries:
                    entry = {
                        "name": item.get("material_id", ""),
                        "Tc": item.get("tc", None),
                        "pressure": item.get("pressure", None),
                        "structure": item.get("structure", {}).get("pretty_formula", ""),
                        "synthesis_method": item.get("synthesis_method", ""),
                        "reference": item.get("reference", ""),
                    }
                    results.append(entry)
                return results
        except Exception as e:
            print(f"Error querying Materials Project: {e}", file=sys.stderr)
            sys.exit(1)
    elif db_name == "supercon":
        base_url = "https://supercon.nims.go.jp/api/search"
        query_params = {}
        if params.get("name"):
            query_params["name"] = params["name"]
        if params.get("composition"):
            query_params["composition"] = params["composition"]
        if params.get("tc_min") is not None:
            query_params["tc_min"] = params["tc_min"]
        if params.get("tc_max") is not None:
            query_params["tc_max"] = params["tc_max"]
        if params.get("pressure") is not None:
            query_params["pressure"] = params["pressure"]
        if params.get("synthesis_method"):
            query_params["synthesis_method"] = params["synthesis_method"]
        if api_key:
            query_params["api_key"] = api_key
        url = base_url + "?" + urllib.parse.urlencode(query_params)
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                results = []
                for item in data:
                    entry = {
                        "name": item.get("name", ""),
                        "Tc": item.get("Tc", None),
                        "pressure": item.get("pressure", None),
                        "structure": item.get("structure", ""),
                        "synthesis_method": item.get("synthesis_method", ""),
                        "reference": item.get("reference", ""),
                    }
                    results.append(entry)
                return results
        except Exception as e:
            print(f"Error querying SuperCon: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unknown external database: {db_name}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Query superconductor database")
    parser.add_argument("--name", type=str, help="Exact name of superconductor")
    parser.add_argument("--tc-min", type=float, help="Minimum Tc (K)")
    parser.add_argument("--tc-max", type=float, help="Maximum Tc (K)")
    parser.add_argument("--pressure", type=float, help="Pressure (GPa)")
    parser.add_argument("--pressure-min", type=float, help="Minimum pressure (GPa)")
    parser.add_argument("--pressure-max", type=float, help="Maximum pressure (GPa)")
    parser.add_argument("--composition", type=str, help="Composition filter (e.g., 'H3S')")
    parser.add_argument("--synthesis", type=str, help="Synthesis method filter (e.g., 'HPHT')")
    parser.add_argument("--synthesis-method", type=str, help="Synthesis method filter (e.g., 'HPHT')")
    parser.add_argument("--mechanism", type=str, help="Mechanism type filter (e.g., 'BCS', 'unconventional')")
    parser.add_argument("--external-db", type=str, choices=["supercon", "materials_project"], help="Query external database")
    parser.add_argument("--api-key", type=str, help="API key for external database (or set env var)")
    parser.add_argument("--output", type=str, choices=["table", "json", "csv"], default="table", help="Output format (default: table)")
    args = parser.parse_args()

    if args.external_db:
        api_key = args.api_key or os.environ.get("MATERIALS_API_KEY") or os.environ.get("SUPERCON_API_KEY")
        params = {
            "name": args.name,
            "composition": args.composition,
            "tc_min": args.tc_min,
            "tc_max": args.tc_max,
            "pressure": args.pressure,
            "pressure_min": args.pressure_min,
            "pressure_max": args.pressure_max,
            "synthesis_method": args.synthesis_method or args.synthesis,
            "mechanism": args.mechanism,
        }
        results = query_external_database(args.external_db, params, api_key)
        if not results:
            print("No matching superconductors found from external database.")
            return
        if args.output == "json":
            print(json.dumps(results, indent=2, sort_keys=True))
        elif args.output == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Name", "Tc (K)", "Pressure (GPa)", "Structure", "Composition", "Synthesis Method", "Mechanism", "Reference"])
            for r in results:
                writer.writerow([r.get('name', ''), r.get('Tc', ''), r.get('pressure', ''), r.get('structure', ''), r.get('composition', ''), r.get('synthesis_method', ''), r.get('mechanism', ''), r.get('reference', '')])
            print(output.getvalue().strip())
        else:
            print(f"Found {len(results)} superconductor(s) from {args.external_db}:")
            print("-" * 120)
            header = f"{'Name':<20} {'Tc (K)':<10} {'Pressure (GPa)':<15} {'Structure':<20} {'Composition':<20} {'Synthesis Method':<20} {'Mechanism':<20} {'Reference':<20}"
            print(header)
            print("-" * 120)
            for r in results:
                name = r.get('name', '')
                tc = r.get('Tc', '')
                pressure = r.get('pressure', '')
                structure = r.get('structure', '')
                composition = r.get('composition', '')
                synthesis_method = r.get('synthesis_method', '')
                mechanism = r.get('mechanism', '')
                reference = r.get('reference', '')
                print(f"{name:<20} {tc:<10} {pressure:<15} {structure:<20} {composition:<20} {synthesis_method:<20} {mechanism:<20} {reference:<20}")
            print("-" * 120)
        return

    try:
        entries = load_database(DATABASE_PATH)
    except FileNotFoundError:
        print(f"Error: Database file '{DATABASE_PATH}' not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in database: {e}", file=sys.stderr)
        sys.exit(1)

    results = query(entries, args)

    if not results:
        print("No matching superconductors found.")
        return

    if args.output == "json":
        print(json.dumps(results, indent=2, sort_keys=True))
    elif args.output == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "Tc (K)", "Pressure (GPa)", "Structure", "Composition", "Synthesis Method", "Mechanism", "Reference"])
        for r in results:
            writer.writerow([r.get('name', ''), r.get('Tc', ''), r.get('pressure', ''), r.get('structure', ''), r.get('composition', ''), r.get('synthesis_method', ''), r.get('mechanism', ''), r.get('reference', '')])
        print(output.getvalue().strip())
    else:
        print(f"Found {len(results)} superconductor(s):")
        print("-" * 120)
        header = f"{'Name':<20} {'Tc (K)':<10} {'Pressure (GPa)':<15} {'Structure':<20} {'Composition':<20} {'Synthesis Method':<20} {'Mechanism':<20} {'Reference':<20}"
        print(header)
        print("-" * 120)
        for r in results:
            name = r.get('name', '')
            tc = r.get('Tc', '')
            pressure = r.get('pressure', '')
            structure = r.get('structure', '')
            composition = r.get('composition', '')
            synthesis_method = r.get('synthesis_method', '')
            mechanism = r.get('mechanism', '')
            reference = r.get('reference', '')
            print(f"{name:<20} {tc:<10} {pressure:<15} {structure:<20} {composition:<20} {synthesis_method:<20} {mechanism:<20} {reference:<20}")
        print("-" * 120)

if __name__ == "__main__":
    main()
