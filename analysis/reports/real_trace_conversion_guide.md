# Real Trace Conversion Guide for The ONE

**Purpose**: Document technical procedures to convert real DTN/OppNet traces into The ONE simulator format.

**Date**: 2026-06-13  
**Scope**: Practical conversion pipelines for contact traces, GPS trajectories, and WiFi logs.

---

## Overview

The ONE supports three main trace input mechanisms:

1. **ExternalEvent** (contact/connectivity traces)
2. **ExternalMovement** (coordinate-based movement)
3. **MapRouteMovement** (road-constrained routing)

This guide maps real datasets to these mechanisms.

---

## Pattern 1: Contact Traces → ExternalEvent

### Applicable Datasets
- DieselNet (buses)
- INFOCOM 2005–2007 (iMote conferences)
- MIT Reality Mining (campus proximity)
- RollerNet (event Bluetooth)
- Cambridge Haggle (mixed indoor/outdoor)

### Input Format (General Contact Trace)

**Standard Format**:
```
timestamp node_a node_b duration_seconds [metadata]
```

**Example (DieselNet)**:
```
0:16:14 PVTA_3201 PVTA_3117 235560.0
```

**Example (Generic)**:
```
1000 5 12 300
1120 5 12 450
1200 7 12 600
```

### The ONE Expected Format (CONN)

```
time CONN node_a node_b up
time CONN node_a node_b down
```

**Example**:
```
1000 CONN 5 12 up
1300 CONN 5 12 down
1120 CONN 5 12 up
1570 CONN 5 12 down
1200 CONN 7 12 up
1800 CONN 7 12 down
```

### Conversion Algorithm

#### Step 1: Parse Input

```python
def parse_contact_trace(file_path):
    """Parse generic contact trace format."""
    contacts = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            timestamp, node_a, node_b, duration = parts[0:4]
            contacts.append({
                'time_start': float(timestamp),
                'node_a': node_a,
                'node_b': node_b,
                'duration': float(duration)
            })
    return contacts
```

#### Step 2: Normalize Node IDs

```python
def normalize_node_ids(contacts):
    """Map string node names to integer IDs."""
    node_map = {}
    next_id = 0
    
    for contact in contacts:
        for key in ['node_a', 'node_b']:
            if contact[key] not in node_map:
                node_map[contact[key]] = next_id
                next_id += 1
    
    normalized = []
    for contact in contacts:
        normalized.append({
            'time_start': contact['time_start'],
            'time_end': contact['time_start'] + contact['duration'],
            'node_a': node_map[contact['node_a']],
            'node_b': node_map[contact['node_b']]
        })
    
    return normalized, node_map
```

#### Step 3: Generate CONN Events

```python
def generate_conn_events(normalized_contacts):
    """Generate CONN format events (up/down pairs)."""
    events = []
    
    for contact in normalized_contacts:
        # Up event (contact starts)
        events.append(f"{int(contact['time_start'])} CONN {contact['node_a']} {contact['node_b']} up")
        
        # Down event (contact ends)
        events.append(f"{int(contact['time_end'])} CONN {contact['node_a']} {contact['node_b']} down")
    
    # Sort by timestamp
    events.sort(key=lambda e: int(e.split()[0]))
    
    return events
```

#### Step 4: Write Output

```python
def write_conn_trace(output_file, events, source_file):
    """Write CONN format trace file."""
    with open(output_file, 'w') as f:
        f.write(f"# Connection trace converted from {source_file}\n")
        f.write(f"# Generated: {datetime.now()}\n\n")
        for event in events:
            f.write(event + '\n')
```

### Example: DieselNet Conversion

**Input** (DieselNet Fall 2007):
```
PVTA_3201 PVTA_3117 0:16:14 235560.0 584.0 42.38768 -72.52352
PVTA_3201 PVTA_3222 0:25:30 115000.0 200.0 42.39123 -72.51234
```

**Processing**:
1. Parse: Extract timestamp (0:16:14 = 974 sec), node IDs (PVTA_3201, PVTA_3117), duration (235560 sec)
2. Normalize: PVTA_3201 → 0, PVTA_3117 → 1, PVTA_3222 → 2
3. Generate events:
   ```
   974 CONN 0 1 up
   236534 CONN 0 1 down
   1530 CONN 0 2 up
   116530 CONN 0 2 down
   ```

**Note**: The existing `toolkit/dieselnetConverter.pl` implements this (Perl). Use it directly:

```bash
perl toolkit/dieselnetConverter.pl -out output_trace.txt -first 0 input_dieselnet.txt
```

### Configuration in .settings

```properties
# Load contact trace
ExternalEvent1.class = ExternalEvent
ExternalEvent1.filePath = path/to/output_trace.txt
```

### Validation

**Checks**:
- ✓ All node IDs are non-negative integers
- ✓ Up/down events are paired (no orphaned "up" or unpaired "down")
- ✓ time_end > time_start for each contact
- ✓ No time reversals (events sorted by timestamp)
- ✓ No duplicate simultaneous events

**Python Validation Script**:

```python
def validate_conn_trace(file_path):
    """Validate CONN format trace."""
    nodes = set()
    events = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) != 5:
                print(f"Invalid line: {line}")
                return False
            time, conn_type, node_a, node_b, direction = parts
            if conn_type != 'CONN':
                print(f"Invalid event type: {conn_type}")
                return False
            if direction not in ['up', 'down']:
                print(f"Invalid direction: {direction}")
                return False
            nodes.add(int(node_a))
            nodes.add(int(node_b))
            events.append((int(time), int(node_a), int(node_b), direction))
    
    # Check for orphaned events
    up_down_pairs = {}
    for time, na, nb, direction in events:
        key = (min(na, nb), max(na, nb))  # Normalize pair
        if direction == 'up':
            if key in up_down_pairs:
                print(f"Multiple 'up' for pair {key} at time {time}")
                return False
            up_down_pairs[key] = time
        else:  # down
            if key not in up_down_pairs:
                print(f"'Down' without 'up' for pair {key} at time {time}")
                return False
            del up_down_pairs[key]
    
    if up_down_pairs:
        print(f"Unclosed 'up' events: {up_down_pairs}")
        return False
    
    print(f"✓ Valid CONN trace: {len(nodes)} nodes, {len(events)} events")
    return True
```

### Limitations

- **No spatial information**: Contact traces don't include node locations
- **No coordination**: Multiple simultaneous contacts may not be physically realistic
- **Implicit mobility**: Assumes mobility model generates correct topology patterns
- **Scalability**: Large traces (10k+ events) can slow simulation

---

## Pattern 2: GPS Trajectories → ExternalMovement

### Applicable Datasets
- SF Taxi Cabspotting
- NYC Taxi (TLC)
- Shanghai Taxi (if available)
- Any GPS/GNSS trajectory data

### Input Format (GPS Traces)

**Standard Format**:
```
timestamp latitude longitude [speed] [heading] [accuracy]
```

**Example (Cabspotting CSV)**:
```
2008-03-01 10:15:00,-122.419, 37.775,0,0,0
2008-03-01 10:15:05,-122.418, 37.776,5,120,5
2008-03-01 10:15:10,-122.417, 37.777,10,125,3
```

### The ONE Expected Format (ExternalMovement)

```
time node_id x y
```

**Where**:
- `time`: Timestamp (seconds from simulation start)
- `node_id`: Integer node identifier
- `x`, `y`: Coordinates in simulation space (meters)

**Example**:
```
0 0 100.0 200.0
5 0 105.2 204.1
10 0 110.5 208.3
```

### Conversion Algorithm

#### Step 1: Read GPS Data

```python
import csv
from datetime import datetime

def read_gps_trace(csv_file):
    """Read GPS trace from CSV."""
    trajectory = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            trajectory.append({
                'timestamp': datetime.fromisoformat(row['datetime']),
                'lat': float(row['latitude']),
                'lon': float(row['longitude']),
                'speed': float(row.get('speed', 0)),
                'node_id': int(row.get('node_id', 0))
            })
    return trajectory
```

#### Step 2: Coordinate Transformation

**Challenge**: GPS (lat, lon) → simulation coordinates (x, y)

**Solution**: Mercator Projection (approximate, good for limited areas):

```python
import math

def lat_lon_to_xy(lat, lon, ref_lat, ref_lon, scale=111320.0):
    """
    Convert lat/lon to x/y using Mercator projection.
    
    Args:
        lat, lon: Coordinates in decimal degrees
        ref_lat, ref_lon: Reference point (e.g., city center)
        scale: Meters per degree (approx 111320 at equator)
    
    Returns:
        x, y: Meters from reference point
    """
    x = (lon - ref_lon) * scale * math.cos(math.radians(ref_lat))
    y = (lat - ref_lat) * scale
    return x, y

# Example: SF area (center ~37.77, -122.42)
ref_lat, ref_lon = 37.77, -122.42
x, y = lat_lon_to_xy(37.775, -122.419, ref_lat, ref_lon)
# Result: x ≈ 730, y ≈ -555 meters
```

**Note**: For large areas (>100 km), use UTM projection instead.

#### Step 3: Temporal Normalization

**Challenge**: GPS timestamps may span days; simulation may start at t=0.

**Solution**:

```python
def normalize_times(trajectory):
    """Normalize timestamps to seconds from simulation start."""
    if not trajectory:
        return trajectory
    
    start_time = trajectory[0]['timestamp']
    for point in trajectory:
        delta = point['timestamp'] - start_time
        point['sim_time'] = delta.total_seconds()
    
    return trajectory
```

#### Step 4: Interpolation / Decimation

**Challenge**: GPS traces often have 1–5 second intervals; simulation may need coarser resolution.

**Solution**:

```python
def decimate_trajectory(trajectory, target_interval=10):
    """Downsample trajectory to target interval (seconds)."""
    decimated = []
    last_time = None
    
    for point in trajectory:
        if last_time is None or point['sim_time'] - last_time >= target_interval:
            decimated.append(point)
            last_time = point['sim_time']
    
    return decimated
```

#### Step 5: Generate ExternalMovement File

```python
def generate_external_movement(trajectory, output_file, node_id=0):
    """Generate ExternalMovement format."""
    with open(output_file, 'w') as f:
        f.write("# External movement trace converted from GPS\n")
        f.write(f"# Node ID: {node_id}\n")
        f.write(f"# Format: time(s) node_id x(m) y(m)\n\n")
        
        for point in trajectory:
            time = int(point['sim_time'])
            x = point['x']
            y = point['y']
            f.write(f"{time} {node_id} {x:.1f} {y:.1f}\n")
```

### Example: SF Taxi Conversion

**Input (Cabspotting subset)**:
```
2008-03-01 10:00:00,-122.4200, 37.7750,0,0,0
2008-03-01 10:00:05,-122.4195, 37.7752,8,42,5
2008-03-01 10:00:10,-122.4190, 37.7755,10,45,3
```

**Processing**:
1. Normalize times: (0s, 5s, 10s from simulation start)
2. Convert coordinates (Mercator, ref point SF center):
   - (37.775, -122.420) → (100, 0) m
   - (37.7752, -122.4195) → (142, 222) m
   - (37.7755, -122.4190) → (188, 444) m
3. Output:
   ```
   0 0 100.0 0.0
   5 0 142.0 222.0
   10 0 188.0 444.0
   ```

### Configuration in .settings

```properties
Group.movementModel = ExternalMovement
Group.externalMovementFile = path/to/trajectory.txt
```

### Validation

**Checks**:
- ✓ Coordinates within world bounds (0 to worldSize)
- ✓ Velocity reasonable (max ~50 m/s = 180 km/h for cars)
- ✓ No negative times
- ✓ Times monotonically increasing
- ✓ Sampling sufficient (not too sparse)

**Python Validation Script**:

```python
def validate_external_movement(file_path, world_size=1000, max_velocity=50):
    """Validate ExternalMovement format."""
    prev_time = 0
    prev_x, prev_y = None, None
    num_points = 0
    
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.strip().split()
            if len(parts) != 4:
                print(f"Invalid line: {line}")
                return False
            
            try:
                time, node_id, x, y = int(parts[0]), int(parts[1]), float(parts[2]), float(parts[3])
            except ValueError:
                print(f"Parse error: {line}")
                return False
            
            # Check bounds
            if x < 0 or x > world_size or y < 0 or y > world_size:
                print(f"Out of bounds: ({x}, {y}) at time {time}")
                return False
            
            # Check time order
            if time < prev_time:
                print(f"Time reversal: {time} < {prev_time}")
                return False
            
            # Check velocity
            if prev_x is not None and time > prev_time:
                distance = math.sqrt((x - prev_x)**2 + (y - prev_y)**2)
                velocity = distance / (time - prev_time)
                if velocity > max_velocity:
                    print(f"Excessive velocity: {velocity} m/s at time {time}")
                    return False
            
            prev_time, prev_x, prev_y = time, x, y
            num_points += 1
    
    print(f"✓ Valid ExternalMovement: {num_points} points")
    return True
```

### Limitations

- **Limited history**: Trajectory traces don't capture node context (why at location X?)
- **Scalability**: Large traces (millions of points) consume memory
- **Spatial resolution**: GPS accuracy ~5–10 m; simulation may operate at meter scale
- **No contact inference**: GPS alone doesn't determine wireless contacts (requires proximity model)

---

## Pattern 3: WiFi Association → Derived Contact Trace

### Applicable Datasets
- UCSD WiFi (CED)
- NUS WiFi/Bluetooth
- Other campus WiFi traces

### Input Format (WiFi Association Log)

**Standard Format**:
```
timestamp device_id access_point_id [signal_strength] [other_fields]
```

**Example**:
```
2023-01-01 10:00:00 device_001 AP_building1_floor2 -65
2023-01-01 10:00:01 device_001 AP_building1_floor2 -64
2023-01-01 10:00:05 device_002 AP_building1_floor2 -70
2023-01-01 10:00:10 device_001 AP_building2_floor1 -60
```

### Conversion Challenge

**Problem**: WiFi logs record AP associations, not direct peer contacts.

**Assumption**: Devices associated with the same AP at overlapping times are "in contact".

**Algorithm**:

```python
def derive_contacts_from_wifi(wifi_log_file, time_window=60):
    """
    Derive contact pairs from WiFi association logs.
    
    Devices are considered in contact if:
    - Both associated with same AP
    - Time windows overlap (within time_window seconds)
    """
    # Parse WiFi log
    associations = {}  # device_id -> [(time, ap_id), ...]
    
    with open(wifi_log_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split()
            timestamp = datetime.fromisoformat(f"{parts[0]} {parts[1]}")
            device_id = parts[2]
            ap_id = parts[3]
            
            if device_id not in associations:
                associations[device_id] = []
            associations[device_id].append({
                'time': timestamp,
                'ap': ap_id
            })
    
    # Find co-located devices
    contacts = []
    device_ids = sorted(associations.keys())
    
    for i, dev_a in enumerate(device_ids):
        for dev_b in device_ids[i+1:]:
            # Find time windows where both at same AP
            for assoc_a in associations[dev_a]:
                for assoc_b in associations[dev_b]:
                    if assoc_a['ap'] != assoc_b['ap']:
                        continue
                    
                    # Check time overlap
                    time_diff = abs((assoc_a['time'] - assoc_b['time']).total_seconds())
                    if time_diff <= time_window:
                        contacts.append({
                            'time_start': min(assoc_a['time'], assoc_b['time']),
                            'device_a': dev_a,
                            'device_b': dev_b,
                            'duration': time_window,  # Approximate
                            'ap': assoc_a['ap']
                        })
    
    return contacts
```

### Limitations

- **Indirect measurement**: Can't measure direct proximity (AP-mediated contact)
- **Time window assumption**: Arbitrary (60 sec default may not match real contact range)
- **No fine-grained timing**: WiFi logs often aggregated (no sub-second precision)
- **AP location unknown**: Can't validate contact distance

### Recommendation

WiFi traces are useful for **contact rate validation** but not **spatial accuracy**. Use only if:
1. No direct proximity data available
2. Contact graph topology is primary research question
3. You're willing to accept AP-mediated contact model

---

## Multi-Node Trajectory Files

### When You Have Multiple Nodes

If converting a trace with many nodes (e.g., SF Taxi ~500), you may have:
- Option A: Single file, all nodes
- Option B: One file per node

**The ONE Support**: Both ✓

**Recommended Format** (single file):

```
# External movement trace - SF Taxi Cabspotting
# Converted: 2026-06-13
# Total nodes: 500
# Duration: 30 days (2.592 Ms)

0 0 100.0 200.0
5 0 105.2 204.1
10 0 110.5 208.3
0 1 150.0 250.0
5 1 155.3 254.2
...
```

**Multiple Groups in .settings**:

```properties
Group1.groupId = taxi
Group1.nrofHosts = 500
Group1.movementModel = ExternalMovement
Group1.externalMovementFile = path/to/trajectory_all_taxis.txt
```

---

## Summary: Conversion Decision Tree

```
Real Trace Type?
│
├─ Contact Traces (direct measurement)
│  └─ → Pattern 1: ExternalEvent + CONN format
│     ├─ Example: DieselNet (use existing converter)
│     ├─ Best for: Protocol routing/caching validation
│     └─ Limitation: No spatial info
│
├─ GPS Trajectories
│  └─ → Pattern 2: ExternalMovement + interpolation
│     ├─ Example: SF Taxi Cabspotting
│     ├─ Best for: Mobility model validation
│     └─ Limitation: Doesn't determine contacts directly
│
└─ WiFi/BT Association Logs
   └─ → Pattern 3: Derived contacts via co-location
      ├─ Example: UCSD WiFi campus
      ├─ Best for: Contact topology validation
      └─ Limitation: Indirect, requires assumptions
```

---

## Best Practices

1. **Always validate** before simulation (use provided scripts)
2. **Document assumptions** (coordinate systems, time windows, etc.)
3. **Test with small subset first** (e.g., 1 day, 10 nodes)
4. **Compare synthetic baseline** (RWP, default model) against converted trace
5. **Report metrics** (contact rate, duration, intercontact time) for comparison

---

## Tools & Scripts

**Location**: `toolkit/`
- `dieselnetConverter.pl` — DieselNet to CONN
- Add GPS→ExternalMovement converter (to be written)
- Add WiFi→Contact converter (to be written)

**Future Work**: Contribute converters back to The ONE project (GitHub).

---

**Document Version**: 1.0  
**Last Updated**: 2026-06-13
