#pragma once
#include <Arduino.h>
#include <SHA256.h>
#include "Packet.h"

#define REGION_MAX_ENTRIES    4
#define REGION_NAME_LEN       16
#define REGION_KEY_LEN        16
#define REGION_DENY_FLOOD     0x01

struct RegionEntry {
    char name[REGION_NAME_LEN];
    uint8_t flags;
    uint8_t key[REGION_KEY_LEN];    // SHA256(name) truncated to 16 bytes
};

class RegionMap {
private:
    uint8_t _count;
    RegionEntry _entries[REGION_MAX_ENTRIES];
    RegionEntry _wildcard;    // Always present, name = "*"

    void deriveKey(const char* name, uint8_t* key) {
        SHA256 sha;
        sha.reset();
        sha.update(name, strlen(name));
        uint8_t hash[32];
        sha.finalize(hash, sizeof(hash));
        memcpy(key, hash, REGION_KEY_LEN);
    }

    // Compute expected transport code for a packet using region key
    uint16_t calcTransportCode(const uint8_t* key, const MCPacket* pkt) {
        SHA256 sha;
        sha.resetHMAC(key, REGION_KEY_LEN);
        uint8_t ptype = pkt->header.getPayloadType();
        sha.update(&ptype, 1);
        sha.update(pkt->payload, pkt->payloadLen);
        uint16_t code;
        sha.finalizeHMAC(key, REGION_KEY_LEN, &code, 2);
        if (code == 0x0000) code = 0x0001;
        if (code == 0xFFFF) code = 0xFFFE;
        return code;
    }

public:
    RegionMap() : _count(0) {
        memset(_entries, 0, sizeof(_entries));
        memset(&_wildcard, 0, sizeof(_wildcard));
        _wildcard.name[0] = '*';
        _wildcard.name[1] = '\0';
        _wildcard.flags = 0;    // Default: allow flood
    }

    RegionEntry& getWildcard() { return _wildcard; }
    uint8_t getCount() const { return _count; }
    const RegionEntry* getEntry(uint8_t i) const {
        return (i < _count) ? &_entries[i] : nullptr;
    }

    // Find region matching packet transport codes
    // Returns entry pointer (allow) or NULL (deny/no match)
    RegionEntry* findMatch(const MCPacket* pkt, uint8_t denyMask) {
        for (uint8_t i = 0; i < _count; i++) {
            uint16_t expected = calcTransportCode(_entries[i].key, pkt);
            if (expected == pkt->transport_codes[0]) {
                if (_entries[i].flags & denyMask) return nullptr;
                return &_entries[i];
            }
        }
        // No specific match — check wildcard
        if (_wildcard.flags & denyMask) return nullptr;
        return &_wildcard;
    }

    // Add or update a region entry
    bool put(const char* name) {
        if (!name || name[0] == '\0') return false;
        // Check if already exists
        for (uint8_t i = 0; i < _count; i++) {
            if (strncmp(_entries[i].name, name, REGION_NAME_LEN - 1) == 0) {
                return true;    // Already exists
            }
        }
        if (_count >= REGION_MAX_ENTRIES) return false;
        strncpy(_entries[_count].name, name, REGION_NAME_LEN - 1);
        _entries[_count].name[REGION_NAME_LEN - 1] = '\0';
        _entries[_count].flags = 0;
        deriveKey(name, _entries[_count].key);
        _count++;
        return true;
    }

    // Remove a region entry by name
    bool remove(const char* name) {
        for (uint8_t i = 0; i < _count; i++) {
            if (strncmp(_entries[i].name, name, REGION_NAME_LEN - 1) == 0) {
                // Shift remaining entries
                for (uint8_t j = i; j < _count - 1; j++) {
                    _entries[j] = _entries[j + 1];
                }
                _count--;
                memset(&_entries[_count], 0, sizeof(RegionEntry));
                return true;
            }
        }
        return false;
    }

    // Set/clear deny flood flag
    bool allowFlood(const char* name) {
        if (name[0] == '*') { _wildcard.flags &= ~REGION_DENY_FLOOD; return true; }
        for (uint8_t i = 0; i < _count; i++) {
            if (strncmp(_entries[i].name, name, REGION_NAME_LEN - 1) == 0) {
                _entries[i].flags &= ~REGION_DENY_FLOOD;
                return true;
            }
        }
        return false;
    }

    bool denyFlood(const char* name) {
        if (name[0] == '*') { _wildcard.flags |= REGION_DENY_FLOOD; return true; }
        for (uint8_t i = 0; i < _count; i++) {
            if (strncmp(_entries[i].name, name, REGION_NAME_LEN - 1) == 0) {
                _entries[i].flags |= REGION_DENY_FLOOD;
                return true;
            }
        }
        return false;
    }

    void clear() {
        _count = 0;
        memset(_entries, 0, sizeof(_entries));
        _wildcard.flags = 0;
    }
};
