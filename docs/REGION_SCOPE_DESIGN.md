# Region & Scope System - Design Document

**Version:** 0.8.0 (in development)
**MeshCore Compatibility:** 1.10.0+
**Status:** Design Phase
**Author:** Andrea Bernardi

---

## Overview

This document describes the implementation of the **Region & Scope** system for CubeCellMeshCore, providing MeshCore 1.10.0+ compatibility for geographic packet filtering.

### Goals

1. **Region Filtering** - Limit packet forwarding based on geographic scope
2. **Backward Compatibility** - Maintain compatibility with older MeshCore firmware via wildcard `*`
3. **Resource Efficiency** - Minimal Flash/RAM impact on constrained hardware
4. **Standard Compliance** - Full MeshCore 1.10.0+ protocol support

---

## MeshCore Protocol Background

### Transport Codes & Scope

MeshCore 1.10.0+ introduced **scope filtering** via transport codes in packet headers:

- **Route Types with Scope Support:**
  - `MC_ROUTE_TRANSPORT_FLOOD` (0x00) - Flood with scope/transport codes
  - `MC_ROUTE_TRANSPORT_DIRECT` (0x03) - Direct with scope/transport codes

- **Legacy Route Types (no scope):**
  - `MC_ROUTE_FLOOD` (0x01) - Traditional flood routing
  - `MC_ROUTE_DIRECT` (0x02) - Traditional direct routing

### Scope Format

Scope is encoded in the packet path as **transport codes**:
- Format: `[scope_length][scope_string]` before hop entries
- Example: `0x05 "us-co"` = scope "us-co" (5 bytes)
- No scope = empty scope = matches wildcard `*`

### Region Matching Rules

1. **Exact Match**: Repeater forwards if scope exactly matches a configured region
2. **Wildcard Match**: Repeater with `*` forwards ALL packets (backward compat)
3. **Hierarchical Match**: `us-co` matches both `us` and `us-co`
4. **No Scope**: Packets without scope always propagate (backward compat)

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Region & Scope System                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  RegionManager   │◄────────│   NodeConfig     │     │
│  │                  │         │   (EEPROM v5)    │     │
│  │  - addRegion()   │         │                  │     │
│  │  - removeRegion()│         │  regionCount: 8  │     │
│  │  - hasRegion()   │         │  regions[8][8]   │     │
│  │  - matchScope()  │         │  + wildcard "*"  │     │
│  └────────┬─────────┘         └──────────────────┘     │
│           │                                              │
│           │                                              │
│  ┌────────▼──────────────────────────────────────┐     │
│  │         Packet Forwarding Logic                │     │
│  │                                                 │     │
│  │  1. Parse transport codes from path            │     │
│  │  2. Extract scope string                       │     │
│  │  3. Check RegionManager.matchScope()          │     │
│  │  4. Forward if match OR wildcard present      │     │
│  └─────────────────────────────────────────────────┘     │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │           CLI Commands                           │    │
│  │                                                  │    │
│  │  - get region                                   │    │
│  │  - set region <code>                           │    │
│  │  - add region <code>                           │    │
│  │  - remove region <code>                        │    │
│  │  - list regions                                │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Data Structures

### NodeConfig Extension (v5)

```cpp
// main.h / Config.h
#define EEPROM_VERSION      5           // Bumped from 4
#define MC_MAX_REGIONS      8           // Max regions per repeater
#define MC_REGION_LEN       8           // Max region code length

struct NodeConfig {
    // ... existing fields ...

    // Region & Scope support (v5) - MeshCore 1.10.0+
    uint8_t regionCount;                                    // 0-8
    char regions[MC_MAX_REGIONS][MC_REGION_LEN];           // e.g., "us", "us-co", "*"
    uint8_t reserved[1];                                    // Was [3]
};
```

**Memory Impact:**
- `regionCount`: 1 byte
- `regions`: 8 × 8 = 64 bytes
- **Total**: 65 bytes added to NodeConfig
- **New NodeConfig size**: ~175 bytes (was ~110 bytes)
- **EEPROM availability**: 512 bytes total, ~300 used after this change

### RegionManager Class

New file: `src/mesh/RegionManager.h`

```cpp
#pragma once
#include <Arduino.h>

#define REGION_WILDCARD "*"

class RegionManager {
private:
    uint8_t regionCount;
    char regions[MC_MAX_REGIONS][MC_REGION_LEN];

public:
    RegionManager();

    // Region management
    bool addRegion(const char* region);
    bool removeRegion(const char* region);
    bool hasRegion(const char* region) const;
    uint8_t getRegionCount() const;
    const char* getRegion(uint8_t index) const;
    void clear();

    // Scope matching
    bool matchScope(const char* scope) const;
    bool hasWildcard() const;

    // Load/Save from NodeConfig
    void loadFromConfig(const NodeConfig* config);
    void saveToConfig(NodeConfig* config) const;

    // Validation
    static bool isValidRegionCode(const char* code);

private:
    bool hasRegionInternal(const char* region) const;
    static bool regionsMatch(const char* region, const char* scope);
};
```

---

## Implementation Plan

### Phase 1: Core Infrastructure ✅ (Current)

**Status:** Completed in this session

- [x] Extended NodeConfig with regions array
- [x] Updated EEPROM_VERSION to 5
- [x] Added default wildcard `*` for backward compatibility
- [x] Updated Config.h and Config.cpp structures

**Files Modified:**
- `src/main.h` - Added MC_MAX_REGIONS, MC_REGION_LEN defines
- `src/core/Config.h` - Updated NodeConfig struct, EEPROM_VERSION
- `src/core/Config.cpp` - Updated defaultConfig initialization

### Phase 2: RegionManager Implementation

**To Do:**
1. Create `src/mesh/RegionManager.h` with full class implementation
2. Implement region validation (lowercase, max 7 chars, alphanumeric + dash)
3. Implement scope matching logic:
   - Exact match: `"us-co"` matches `"us-co"`
   - Hierarchical match: `"us-co"` matches `"us"`
   - Wildcard match: `"*"` matches everything
4. Add load/save from NodeConfig

**Key Methods:**

```cpp
bool RegionManager::matchScope(const char* scope) const {
    // Empty scope always matches (backward compat)
    if (!scope || scope[0] == '\0') return true;

    // Wildcard matches everything
    if (hasWildcard()) return true;

    // Check exact and hierarchical matches
    for (uint8_t i = 0; i < regionCount; i++) {
        if (regionsMatch(regions[i], scope)) {
            return true;
        }
    }

    return false;
}

bool RegionManager::regionsMatch(const char* region, const char* scope) {
    // Exact match
    if (strcmp(region, scope) == 0) return true;

    // Hierarchical match: "us" matches "us-co", "us-ca", etc.
    size_t regionLen = strlen(region);
    if (strncmp(region, scope, regionLen) == 0 &&
        scope[regionLen] == '-') {
        return true;
    }

    return false;
}
```

### Phase 3: Packet Format Support

**To Do:**
1. Add transport code parsing to Packet.h:
   ```cpp
   struct TransportCodes {
       uint8_t scopeLen;
       char scope[32];
       bool valid;
   };

   bool parseTransportCodes(const uint8_t* path, uint8_t pathLen,
                           TransportCodes* tc);
   ```

2. Update MCPacket deserialization for TRANSPORT route types
3. Extract scope from path when route type is TRANSPORT_FLOOD or TRANSPORT_DIRECT

### Phase 4: Forwarding Logic Integration

**To Do:**
1. Update `shouldForward()` in main.cpp:
   ```cpp
   bool shouldForward(MCPacket* pkt) {
       // ... existing checks ...

       // Region & Scope filtering (MeshCore 1.10.0+)
       if (pkt->header.getRouteType() == MC_ROUTE_TRANSPORT_FLOOD ||
           pkt->header.getRouteType() == MC_ROUTE_TRANSPORT_DIRECT) {
           TransportCodes tc;
           if (parseTransportCodes(pkt->path, pkt->pathLen, &tc)) {
               if (!regionManager.matchScope(tc.scope)) {
                   LOG("[FW] Scope '%s' not in regions, drop\n\r", tc.scope);
                   return false;
               }
           }
       }

       return true;
   }
   ```

2. Update loop detection to handle transport codes correctly

### Phase 5: CLI Commands

**To Do:**
Add commands to main.cpp:

```cpp
// Get current regions
if (strcmp(cmd, "get region") == 0 || strcmp(cmd, "regions") == 0) {
    CP("Regions: %d\n\r", regionManager.getRegionCount());
    for (uint8_t i = 0; i < regionManager.getRegionCount(); i++) {
        CP(" %d: %s\n\r", i + 1, regionManager.getRegion(i));
    }
}

// Set primary region (replaces all, adds wildcard)
else if (strncmp(cmd, "set region ", 11) == 0) {
    const char* code = cmd + 11;
    if (RegionManager::isValidRegionCode(code)) {
        regionManager.clear();
        regionManager.addRegion(code);
        regionManager.addRegion("*");  // Always keep wildcard
        regionManager.saveToConfig(&config);
        saveConfig();
        CP("Region set: %s\n\r", code);
    } else {
        CP("Invalid region code\n\r");
    }
}

// Add additional region
else if (strncmp(cmd, "add region ", 11) == 0) {
    const char* code = cmd + 11;
    if (regionManager.addRegion(code)) {
        regionManager.saveToConfig(&config);
        saveConfig();
        CP("Region added: %s\n\r", code);
    } else {
        CP("Failed (max %d regions)\n\r", MC_MAX_REGIONS);
    }
}

// Remove region
else if (strncmp(cmd, "remove region ", 14) == 0) {
    const char* code = cmd + 14;
    if (strcmp(code, "*") == 0) {
        CP("Cannot remove wildcard\n\r");
    } else if (regionManager.removeRegion(code)) {
        regionManager.saveToConfig(&config);
        saveConfig();
        CP("Region removed: %s\n\r", code);
    } else {
        CP("Region not found\n\r");
    }
}

// List regions (alias)
else if (strcmp(cmd, "list regions") == 0) {
    // Same as "get region"
}
```

### Phase 6: Config Load/Save Integration

**To Do:**
1. Update `loadConfig()` in Config.cpp:
   ```cpp
   void loadConfig() {
       // ... existing code ...

       // Load regions
       regionManager.loadFromConfig(&config);

       CONFIG_LOG("[C] Loaded %d region(s)\n\r",
                  regionManager.getRegionCount());
   }
   ```

2. Update `saveConfig()` in Config.cpp:
   ```cpp
   void saveConfig() {
       // ... existing code ...

       // Save regions
       regionManager.saveToConfig(&config);

       // ... commit to EEPROM ...
   }
   ```

3. Update `resetConfig()` to reset regions to wildcard only

### Phase 7: Global Variables

**To Do:**
Add to `src/core/globals.h`:
```cpp
// Region & Scope Manager (MeshCore 1.10.0+)
extern RegionManager regionManager;
```

Add to `src/core/globals.cpp`:
```cpp
#include "../mesh/RegionManager.h"
RegionManager regionManager;
```

### Phase 8: Testing

**To Do:**
Create `tools/test_region_scope.py`:

```python
#!/usr/bin/env python3
"""Test script for Region & Scope system"""

def test_region_validation():
    """Test valid region code formats"""
    valid = ["us", "us-co", "eu", "eu-it", "au", "*"]
    invalid = ["US", "us_co", "us-colorado", "", "123"]
    # Test each...

def test_scope_matching():
    """Test scope matching logic"""
    # Test exact match
    # Test hierarchical match
    # Test wildcard match
    # Test empty scope

def test_cli_commands():
    """Test CLI region commands"""
    # Test get region
    # Test set region
    # Test add region
    # Test remove region
    # Test validation

def test_packet_filtering():
    """Test packet forwarding with scope"""
    # Test TRANSPORT_FLOOD packets
    # Test TRANSPORT_DIRECT packets
    # Test legacy packets (no scope)

if __name__ == '__main__':
    run_all_tests()
```

### Phase 9: Documentation

**To Do:**
1. Update `docs/API.md` with RegionManager API
2. Update `release/COMMANDS.md` with region commands
3. Update `README.md` changelog for v0.8.0
4. Add examples to documentation

---

## Usage Examples

### Example 1: Single Region Repeater (US-Colorado)

```bash
# Configure repeater for Colorado only
> set region us-co
Region set: us-co

> get region
Regions: 2
 1: us-co
 2: *
```

**Behavior:**
- Forwards packets with scope `us-co` ✅
- Forwards packets with scope `us` (hierarchical) ✅
- Forwards packets with scope `us-ca` ❌
- Forwards packets with no scope ✅ (backward compat via wildcard)

### Example 2: Multi-Region Repeater (Border)

```bash
# Repeater at US-Mexico border
> set region us
Region set: us

> add region mx
Region added: mx

> get region
Regions: 3
 1: us
 2: mx
 3: *
```

**Behavior:**
- Forwards packets with scope `us`, `us-*`, `mx`, `mx-*` ✅
- Forwards packets with scope `ca` ❌
- Forwards packets with no scope ✅

### Example 3: Global Repeater (Wildcard Only)

```bash
# Default configuration - forwards everything
> get region
Regions: 1
 1: *
```

**Behavior:**
- Forwards ALL packets regardless of scope ✅
- Full backward compatibility with MeshCore < 1.10.0 ✅

---

## Backward Compatibility

### With MeshCore < 1.10.0 (No Scope Support)

1. **Default Wildcard**: Every repeater starts with `*` region
2. **Legacy Packets**: FLOOD/DIRECT packets (no transport codes) always forwarded
3. **No Breaking Changes**: Existing repeaters continue working without updates

### Migration Path

1. **No Action Required**: Existing deployments work as-is with wildcard
2. **Gradual Adoption**: Admins can add specific regions when needed
3. **Wildcard Removal**: Can optionally remove `*` for strict filtering

---

## Performance Considerations

### Memory Usage

| Component | Size | Location |
|-----------|------|----------|
| NodeConfig extension | +65 bytes | EEPROM |
| RegionManager instance | ~80 bytes | RAM |
| Scope parsing buffer | 32 bytes | Stack (temporary) |
| **Total Impact** | **~177 bytes** | **~0.1% of total** |

### CPU Impact

- **Scope matching**: O(n) where n = number of regions (max 8)
- **Cost per packet**: ~50-100 µs on ARM Cortex-M0+
- **Negligible impact**: < 0.01% CPU usage at 100 pkt/min

### Flash Impact

Estimated code size:
- RegionManager class: ~1.5 KB
- Packet parsing additions: ~0.5 KB
- CLI commands: ~1.0 KB
- **Total**: ~3 KB (~2.3% of available Flash)

---

## Security Considerations

### Validation

- **Region codes**: Lowercase alphanumeric + dash, max 7 chars
- **Scope strings**: Validated before matching, max 31 chars
- **Injection protection**: No dynamic code execution, string ops only

### Access Control

- **Admin only**: Region configuration requires admin password
- **Remote commands**: Available via encrypted mesh CLI
- **No guest access**: Guests cannot modify regions

---

## Testing Strategy

### Unit Tests

1. Region code validation
2. Scope matching logic (exact, hierarchical, wildcard)
3. Config load/save
4. CLI command parsing

### Integration Tests

1. Packet forwarding with various scopes
2. Backward compatibility with legacy packets
3. Multi-region configurations
4. EEPROM persistence across reboots

### Field Tests

1. Real-world multi-region deployment
2. Performance monitoring
3. Scope propagation across network
4. Backward compatibility validation

---

## Future Enhancements (v0.9.0+)

### Scope-aware ADVERT

Currently ADVERT packets don't include scope. Future:
- Add region field to ADVERT appdata
- Allow nodes to discover repeater regions
- Optimize routing based on known regions

### Dynamic Region Discovery

- Auto-detect region from received ADVERT packets
- Suggest regions based on neighbour regions
- Consensus-based region configuration

### Advanced Filtering

- Time-based region switching (e.g., mobile repeaters)
- Region priority/preference
- Negative regions (blacklist)

---

## References

### MeshCore Documentation

- [MeshCore Protocol Specification](https://github.com/meshcore-dev/MeshCore)
- [Region & Scope FAQ](https://github.com/meshcore-dev/MeshCore/blob/main/docs/faq.md)
- [Packet Format Documentation](https://github.com/meshcore-dev/MeshCore/blob/main/docs/packet_format.md)

### Related Issues

- MeshCore Issue #1575: Feature request for region scope channel specific
- MeshCore Issue #1747: Docs unclear on region behaviour

---

## Changelog

### 2026-03-06 - Design Document Created
- Completed Phase 1: EEPROM structure extension
- Documented complete implementation plan
- Ready for Phase 2 development

---

## Author

**Andrea Bernardi** - Project creator and lead developer

## License

MIT License - See LICENSE file for details.
