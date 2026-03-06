# Region & Scope System - Design Document

**Version:** 0.8.0 (planned)
**MeshCore Compatibility:** 1.10.0+
**Status:** Design Phase - Not yet implemented
**Author:** Andrea Bernardi

---

## Overview

This document describes the planned implementation of the **Region** system for CubeCellMeshCore, aligned with the actual MeshCore protocol.

### What Regions Are in MeshCore

Regions are a **deny-based flood filtering** mechanism. Each repeater maintains a **RegionMap** — a hierarchical tree of named regions, each with a flag controlling whether flood packets with that transport code should be forwarded or dropped.

Key concepts:
- **Default: forward everything** — regions only restrict, never grant
- **Deny-based** — `REGION_DENY_FLOOD` flag blocks forwarding for a specific region
- **Hierarchical** — regions form a tree (e.g., `*` > `AU` > `AU/NSW` > `AU/NSW/SYD`)
- **Transport codes** — carried in `ROUTE_TYPE_TRANSPORT_FLOOD` (0x00) and `ROUTE_TYPE_TRANSPORT_DIRECT` (0x03) packets, embedded in the path field
- **Backward compatible** — legacy `ROUTE_TYPE_FLOOD` (0x01) packets have no transport code and are always forwarded unless globally disabled

### What Regions Are NOT

- NOT an allow-list of geographic codes (our previous incorrect design)
- NOT ISO country codes like "us-co" or "eu-it"
- NOT a scope matching system with wildcards meaning "forward all"

---

## MeshCore Protocol Reference

### Transport Codes in Packets

When route type is `ROUTE_TYPE_TRANSPORT_FLOOD` (0x00) or `ROUTE_TYPE_TRANSPORT_DIRECT` (0x03), the path field begins with a transport code:

```
path = [transport_code_len (1 byte)] [transport_code (N bytes)] [hop entries...]
```

- `transport_code_len = 0` means no transport code (same as legacy)
- Transport code is a UTF-8 string identifying the region (e.g., `"AU"`, `"AU/NSW"`)

### Packet Forwarding Logic (MeshCore Reference)

```
allowPacketForward(packet):
  1. If global forwarding disabled -> DROP
  2. If flood and path_len >= flood_max (default 64) -> DROP
  3. If flood: call filterRecvFloodPacket()
     - Extract transport code from path
     - Search RegionMap for matching entry
     - If match has REGION_DENY_FLOOD flag -> recv_pkt_region = NULL -> DROP
     - If match without deny flag -> recv_pkt_region = entry -> FORWARD
     - If no match, check wildcard (*) entry -> same logic
     - If recv_pkt_region == NULL -> DROP
  4. FORWARD
```

### CLI Commands (MeshCore Reference)

| Command | Description |
|---------|-------------|
| `region` | List all defined regions and flood permissions |
| `region get {* \| name}` | Show region name, parent, flood status |
| `region put {name} {* \| parent}` | Add/update a region definition |
| `region remove {name}` | Remove region (must have no children) |
| `region allowf {* \| name}` | Allow flood forwarding for region |
| `region denyf {* \| name}` | Deny flood forwarding for region |
| `region home` | Show current home region |
| `region home {* \| name}` | Set home region |
| `region list {allowed\|denied}` | List regions filtered by flood permission |
| `region save` | Persist region map to storage |
| `region load` | Load region hierarchy via serial (multi-line) |

---

## CubeCellMeshCore Implementation Plan

### Hardware Constraints

The HTCC-AB01 (ASR6501) has severe resource limits:
- **Flash:** 131 KB (currently 99.3% used)
- **RAM:** 16 KB (currently 52% used)
- **EEPROM:** 512 bytes (NodeConfig ~110 bytes + Identity ~132 bytes)

A full hierarchical tree is not feasible. We need a **simplified but protocol-correct** implementation.

### Proposed Simplified Design

Instead of a full tree, use a **flat RegionMap** with a small number of entries:

```cpp
#define REGION_MAX_ENTRIES    4    // Max region entries (keep small for RAM/Flash)
#define REGION_NAME_LEN      12   // Max region name length (e.g., "AU/NSW/SYD")
#define REGION_DENY_FLOOD    0x01 // Flag: deny flood forwarding

struct RegionEntry {
    char name[REGION_NAME_LEN];   // Region name (e.g., "AU", "AU/NSW", "*")
    uint8_t flags;                // REGION_DENY_FLOOD etc.
};

struct RegionMap {
    uint8_t count;                              // Number of entries (0 = no filtering)
    RegionEntry entries[REGION_MAX_ENTRIES];     // Flat list
    char home[REGION_NAME_LEN];                 // Home region name
};
```

**Memory cost:** ~54 bytes RAM, ~54 bytes EEPROM

### Matching Logic

```cpp
// Called by allowPacketForward() for flood packets
RegionEntry* filterRecvFloodPacket(const char* transportCode) {
    // No entries = no filtering = forward all (default behavior)
    if (regionMap.count == 0) return &defaultAllowEntry;

    // Search for exact match first, then parent prefixes
    for (int i = 0; i < regionMap.count; i++) {
        if (matchesRegion(regionMap.entries[i].name, transportCode)) {
            if (regionMap.entries[i].flags & REGION_DENY_FLOOD)
                return NULL;  // Denied
            return &regionMap.entries[i];  // Allowed
        }
    }

    // Check wildcard entry
    for (int i = 0; i < regionMap.count; i++) {
        if (strcmp(regionMap.entries[i].name, "*") == 0) {
            if (regionMap.entries[i].flags & REGION_DENY_FLOOD)
                return NULL;
            return &regionMap.entries[i];
        }
    }

    // No match, no wildcard -> forward (permissive default)
    return &defaultAllowEntry;
}

// Region hierarchy match: "AU" matches transport code "AU/NSW"
bool matchesRegion(const char* region, const char* transportCode) {
    size_t rLen = strlen(region);
    if (strncmp(region, transportCode, rLen) == 0) {
        // Exact match or parent prefix (next char must be '/' or '\0')
        char next = transportCode[rLen];
        return (next == '\0' || next == '/');
    }
    return false;
}
```

### Transport Code Extraction from Path

```cpp
// Extract transport code from TRANSPORT_FLOOD/TRANSPORT_DIRECT packet path
bool extractTransportCode(const uint8_t* path, uint8_t pathLen,
                          char* outCode, uint8_t maxLen) {
    if (pathLen < 1) return false;
    uint8_t tcLen = path[0];
    if (tcLen == 0) {
        outCode[0] = '\0';  // No transport code
        return true;
    }
    if (tcLen >= pathLen || tcLen >= maxLen) return false;
    memcpy(outCode, &path[1], tcLen);
    outCode[tcLen] = '\0';
    return true;
}
```

---

## Implementation Phases

### Phase 1: Transport Code Parsing
- Add `extractTransportCode()` to Packet.h
- Parse transport codes from TRANSPORT_FLOOD and TRANSPORT_DIRECT packets
- Log transport codes when received (debug only)
- **No behavioral change** — all packets still forwarded

### Phase 2: RegionMap Data Structure
- Add RegionMap struct to Config.h
- Add EEPROM storage for RegionMap
- Bump EEPROM version
- Default: empty map (0 entries = forward all)

### Phase 3: Forwarding Integration
- Add `filterRecvFloodPacket()` to forwarding logic
- Only filter TRANSPORT_FLOOD packets with non-empty transport codes
- Legacy FLOOD packets unaffected

### Phase 4: CLI Commands (Subset)
- `region` — list entries and permissions
- `region put {name} {parent}` — add/update entry
- `region remove {name}` — remove entry
- `region allowf {name}` — clear DENY_FLOOD flag
- `region denyf {name}` — set DENY_FLOOD flag
- `region home` / `region home {name}` — get/set home
- `region save` — persist to EEPROM

### Phase 5: Testing
- Unit tests for transport code extraction
- Unit tests for region matching (exact, hierarchical, wildcard)
- Integration tests for packet forwarding with deny/allow
- Backward compatibility tests with legacy FLOOD packets

---

## Flash Budget Estimate

| Component | Estimated Size |
|-----------|---------------|
| Transport code parsing | ~200 bytes |
| RegionMap + matching | ~500 bytes |
| EEPROM load/save | ~300 bytes |
| CLI commands | ~800 bytes |
| **Total** | **~1.8 KB** |

With Flash at 99.3%, we have ~900 bytes free. This means:
- Phase 1-3 can likely fit (~1.0 KB)
- Phase 4 (CLI) may require LITE_MODE optimizations or trimming other features
- Consider making region support a compile-time option (`#define ENABLE_REGIONS`)

---

## References

- [MeshCore GitHub](https://github.com/meshcore-dev/MeshCore)
- [MeshCore Repeater CLI Reference](https://github.com/meshcore-dev/MeshCore/wiki/Repeater-&-Room-Server-CLI-Reference)
- [MeshCore Repeater Applications - DeepWiki](https://deepwiki.com/ripplebiz/MeshCore/3.2-repeater-applications)

---

## Changelog

### 2026-03-06 - Design Document Rewritten
- Removed incorrect allow-list geographic scope design
- Aligned with actual MeshCore deny-based RegionMap protocol
- Simplified for HTCC-AB01 hardware constraints
- Added flash budget analysis
