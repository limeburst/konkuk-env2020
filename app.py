import os
import urllib
from dataclasses import asdict
from time import sleep

import click
from flask import Flask, Response, render_template
from influxdb_client import InfluxDBClient, Point
from seoul import Client


INFLUXDB_BUCKET = os.environ['INFLUXDB_BUCKET']
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']
INFLUXDB_URL = os.environ['INFLUXDB_URL']
SEOUL_API_KEY = os.environ['SEOUL_API_KEY']

app = Flask(__name__)
influxdb = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org='-')
write_api = influxdb.write_api()


@app.cli.command()
def collect():
    """Collect air quality measurements."""
    seoul = Client(SEOUL_API_KEY)
    measurements = seoul.get_air_realtime_city()

    for m in measurements:
        click.echo(f"{m.measured_at} {m.station_name} {m.index_value}")
        point = Point("seoul_air_quality") \
            .tag("region_name", m.region_name) \
            .tag("station_name", m.station_name) \
            .field("pm10", m.pm10) \
            .field("pm25", m.pm25) \
            .field("o3", m.o3) \
            .field("no2", m.no2) \
            .field("co", m.co) \
            .field("so2", m.so2) \
            .field("index_value", m.index_value) \
            .field("index_name", m.index_name) \
            .field("index_pollutant", m.index_pollutant)
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
