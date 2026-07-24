"""Revised map-generation pipeline (v2): OSM + synthetic + real-trace roles."""

from __future__ import annotations

__version__ = "2.0.0"

SOURCE_TYPES = ("osm", "synthetic", "trace_reference_synthetic")

GENERATION_ROLES = (
    "evidence_only",
    "osm_anchor_support",
    "parameterize_generator",
    "trace_reference_synthetic",
    "direct_trace_geometry",
    "unsupported_for_generation",
    "future_candidate",
)

CANONICAL_ARCHETYPES = (
    "urban_grid",
    "dense_urban_irregular",
    "campus_compact",
    "compact_residential",
    "corridor_linear",
    "bus_route_urban_suburban",
    "radial_city",
    "hub_and_spoke",
    "sparse_trails",
    "rural_roads",
    "industrial_disrupted",
    "island_or_partitioned",
    "conference_event_compact",
    "clustered_communities",
    "suburban_low_density",
)
