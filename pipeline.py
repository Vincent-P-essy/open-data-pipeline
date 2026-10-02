"""Validate regional energy CSV data and atomically publish a JSON dataset."""
import argparse
import csv
import datetime
import json
import os
import tempfile
from decimal import Decimal, InvalidOperation
from pathlib import Path


def transform(source: Path) -> dict:
    records, keys = [], set()
    with source.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if set(reader.fieldnames or []) != {'date', 'region', 'megawatt_hours'}:
            raise ValueError('Expected date, region and megawatt_hours columns.')
        for line, row in enumerate(reader, 2):
            if len(records) >= 100000:
                raise ValueError('Input exceeds the 100000-record limit.')
            try:
                date = datetime.date.fromisoformat(row['date']).isoformat()
                region = row['region'].strip()
                value = Decimal(row['megawatt_hours'])
                if not region or len(region) > 100 or not value.is_finite() or value < 0:
                    raise ValueError('Invalid region or energy value.')
            except (ValueError, TypeError, AttributeError, InvalidOperation) as exc:
                raise ValueError(f'Invalid row at line {line}: {exc}') from exc
            key = (date, region)
            if key in keys:
                raise ValueError(f'Duplicate date/region at line {line}.')
            keys.add(key)
            records.append({'date': date, 'region': region, 'megawatt_hours': str(value)})
    if not records:
        raise ValueError('Empty datasets are rejected.')
    records.sort(key=lambda x: (x['date'], x['region']))
    return {'record_count': len(records), 'total_megawatt_hours': str(sum((Decimal(x['megawatt_hours']) for x in records), Decimal(0))), 'records': records}


def publish(source: Path, destination: Path) -> dict:
    data = transform(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, indent=2, ensure_ascii=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('destination', type=Path)
    a = p.parse_args()
    try:
        result = publish(a.source, a.destination)
    except (ValueError, OSError) as exc:
        p.error(str(exc))
    print(f'Validated {result["record_count"]} records. Total: {result["total_megawatt_hours"]} MWh.')
    print(f'Published {a.destination}')

if __name__ == '__main__':
    main()
