# CubeCellMeshCore v0.5.1 - Command Reference

Serial console at 115200 baud. Type `help` for command list.

Commands marked **MeshCore** use the standard MeshCore CLI naming. Legacy aliases are kept for backwards compatibility.

## Status & Info

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | Firmware version, node name/hash, uptime, time sync |
| `stats` | Session counters: RX/TX/FWD/ERR, ADV TX/RX, queue length |
| `ver` | Show firmware version **MeshCore** |
| `clock` | Show current time (alias of `time`) **MeshCore** |
| `time` | Show current time and sync status |
| `lifetime` | Persistent stats: boot count, total uptime, RX/TX/FWD |
| `radiostats` | Noise floor, last RSSI/SNR, airtime TX/RX |
| `packetstats` | Packet breakdown: flood/direct RX/TX |
| `telemetry` | Battery mV/%, uptime |
| `identity` | Node name, hash, location, public key |
| `location` | Show current GPS coordinates (read-only) |
| `nodes` | Discovered nodes (hash, name, RSSI, SNR, packet count, last seen) |
| `contacts` | Known contacts with public keys (serial only) |
| `neighbours` / `neighbors` | Direct repeater neighbours (0-hop ADVERTs) |
| `health` | System dashboard: uptime, battery, network, mailbox, alerts, problem nodes |
| `mailbox` | Store-and-forward mailbox status (slots, EEPROM/RAM, age) |
| `power` | Show power mode, RX boost, deep sleep status |
| `powersaving` | Show current power save mode (0/1/2) **MeshCore** |
| `radio` | Show current radio parameters (+ temp radio if active) |
| `rssi` | Show last RSSI and SNR |
| `acl` | Show admin/guest passwords and active session count |
| `set repeat` | Show repeat status and max hops **MeshCore** |
| `set advert.interval` | Show ADVERT interval (minutes) and next scheduled **MeshCore** |
| `set tx` | Show current TX power, max, auto status **MeshCore** |
| `set name` | Show current node name **MeshCore** |

### Legacy read-only aliases (still supported)

| Legacy | New Equivalent |
|--------|----------------|
| `repeat` | `set repeat` |
| `advert interval` | `set advert.interval` |
| `txpower` | `set tx` |
| `name` | `set name` |

## Node Configuration

| Command | Description |
|---------|-------------|
| `set name <name>` | Set node name (1-15 chars), saves to EEPROM **MeshCore** |
| `set lat <latitude>` | Set latitude (decimal, e.g. `45.123456`), saves to EEPROM **MeshCore** |
| `set lon <longitude>` | Set longitude (decimal, e.g. `7.654321`), saves to EEPROM **MeshCore** |
| `set repeat on\|off` | Enable/disable packet repeating |
| `set flood.max <n>` | Set max flood hops (1-15) |
| `mode 0\|1\|2` | Set power mode (0=performance, 1=balanced, 2=powersave) |
| `powersaving on` | Set power save mode 2 (maximum savings) **MeshCore** |
| `powersaving off` | Set power save mode 0 (performance) **MeshCore** |
| `sleep on\|off` | Enable/disable deep sleep |
| `rxboost on\|off` | Enable/disable RX gain boost |
| `nodetype chat\|repeater` | Set node type (serial only) |
| `time <timestamp>` | Set Unix time manually (serial only) |

### Legacy configuration aliases (still supported)

| Legacy | New Equivalent |
|--------|----------------|
| `name <name>` | `set name <name>` |

## Radio

| Command | Description |
|---------|-------------|
| `radio` | Show current radio parameters |
| `set radio <freq>,<bw>,<sf>,<cr>` | Set radio parameters (comma-separated, serial only) **MeshCore** |
| `tempradio <freq> <bw> <sf> <cr>` | Set temporary radio params (space-separated, serial only) |
| `tempradio off` | Restore default radio params |
| `tempradio` | Show temp radio status |

Example: `set radio 869.618,62.5,8,8` or `tempradio 869.618 62.5 8 8`

## TX Power

| Command | Description |
|---------|-------------|
| `set tx` | Show current TX power and auto status **MeshCore** |
| `set tx <dBm>` | Set manual TX power (disables auto) **MeshCore** |
| `set tx auto on` | Enable adaptive TX power **MeshCore** |
| `set tx auto off` | Disable auto, restore max power **MeshCore** |

### Legacy TX power aliases (still supported)

| Legacy | New Equivalent |
|--------|----------------|
| `txpower` | `set tx` |
| `txpower <dBm>` | `set tx <dBm>` |
| `txpower auto on` | `set tx auto on` |
| `txpower auto off` | `set tx auto off` |

## ADVERT & Network

| Command | Description |
|---------|-------------|
| `advert` | Send ADVERT packet immediately (flood) |
| `advert local` | Send ADVERT packet (direct, 0-hop only) |
| `set advert.interval <min>` | Set ADVERT interval in minutes (1-1440) **MeshCore** |
| `set advert.interval` | Show current interval and next scheduled **MeshCore** |
| `ping` | Send broadcast test packet (FLOOD) |
| `ping <hash>` | Directed ping to node by hex hash, auto-PONG reply |
| `trace <hash>` | Trace route to node, shows path and hop count |

### Legacy ADVERT aliases (still supported)

| Legacy | New Equivalent |
|--------|----------------|
| `advert interval <sec>` | `set advert.interval <min>` (note: old uses seconds, new uses minutes) |

## Passwords & Security

| Command | Description |
|---------|-------------|
| `password` | Show admin and guest passwords **MeshCore** |
| `password <pwd>` | Set admin password (serial and remote) **MeshCore** |
| `set guest.password <pwd>` | Set guest password **MeshCore** |

### Legacy password aliases (still supported)

| Legacy (serial) | New Equivalent |
|--------|----------------|
| `passwd` | `password` |
| `passwd admin <pwd>` | `password <pwd>` |
| `passwd guest <pwd>` | `set guest.password <pwd>` |

| Legacy (remote) | New Equivalent |
|--------|----------------|
| `set password <pwd>` | `password <pwd>` |
| `set guest <pwd>` | `set guest.password <pwd>` |

## Store-and-Forward Mailbox

The repeater stores messages for offline nodes and re-delivers them when the node comes back online (sends an ADVERT). Storage: 2 persistent EEPROM slots + 4 volatile RAM slots = 6 messages max, 24h TTL.

| Command | Description |
|---------|-------------|
| `mailbox` | Show mailbox status: used/total, EEPROM (E) and RAM (R) counts |
| `mailbox clear` | Clear all mailbox slots (admin only) |

## Health Monitor

Automatic mesh health monitoring. Checks for offline nodes (>30 min) and sends alerts.

| Command | Description |
|---------|-------------|
| `health` | Dashboard: uptime, battery, online/offline nodes, problem nodes |
| `alert` | Show alert status (on/off, destination) |
| `alert on\|off` | Enable/disable automatic health alerts |
| `alert dest <name>` | Set alert destination (by contact name) |
| `alert clear` | Clear alert configuration |
| `alert test` | Send a test alert (serial only) |

## Daily Report

| Command | Description |
|---------|-------------|
| `report` | Show report status (on/off, time, destination) |
| `report on` | Enable daily report (requires destination key) |
| `report off` | Disable daily report |
| `report test` | Send a test report immediately |
| `report nodes` | Send a nodes report immediately |
| `report time HH:MM` | Set report send time (24h format) |
| `report dest <name>` | Set report destination (by contact name) |
| `report clear` | Clear destination key and disable report |

## Quiet Hours

Reduce forward rate during configurable hours. Requires TimeSync.

| Command | Description |
|---------|-------------|
| `quiet` | Show quiet hours status |
| `quiet <start> <end>` | Set quiet hours (0-23, e.g. `quiet 22 6`) |
| `quiet off` | Disable quiet hours |

## Circuit Breaker

Blocks DIRECT forwarding to neighbours with degraded links (SNR < -10dB). After 5 min, transitions to half-open. Good SNR closes breaker. FLOOD is never blocked.

| Command | Description |
|---------|-------------|
| `cb` | Show count of open circuit breakers |

## Neighbours

| Command | Description |
|---------|-------------|
| `neighbours` / `neighbors` | List direct repeater neighbours |
| `neighbor.remove <hex>` | Remove neighbour by pubkey hex prefix **MeshCore** |

## Rate Limiting

| Command | Description |
|---------|-------------|
| `ratelimit` | Show rate limiter status and blocked counts |
| `ratelimit on\|off` | Enable/disable rate limiting |
| `ratelimit reset` | Reset rate limit counters |

Default limits: Login 5/min, Request 30/min, Forward 100/min.

## Statistics & Maintenance

| Command | Description |
|---------|-------------|
| `clear stats` | Reset session counters (RX/TX/FWD/ERR/ADV) **MeshCore** |
| `savestats` | Force save persistent statistics to EEPROM (serial only) |

## System

| Command | Description |
|---------|-------------|
| `save` | Save configuration to EEPROM |
| `erase` | Reset configuration to factory defaults (alias of `reset`) **MeshCore** |
| `reset` | Reset configuration to factory defaults |
| `reboot` | Restart device |
| `newid` | Generate new Ed25519 identity (serial only) |

## Serial-Only Commands

These commands are only available via USB serial console, not remotely:

| Command | Description |
|---------|-------------|
| `contacts` | List known contacts |
| `contact <hash>` | Show contact details and public key |
| `nodetype chat\|repeater` | Set node type |
| `time <timestamp>` | Set Unix time |
| `newid` | Generate new identity |
| `savestats` | Force save stats to EEPROM |
| `tempradio ...` | Temporary radio parameters |
| `set radio ...` | Set radio parameters |
| `alert test` | Send test alert |
| `msg <name> <message>` | Send direct message to contact |

## Remote Configuration (via MeshCore app)

All shared commands are available remotely via the MeshCore app's encrypted CLI channel.

### Guest-allowed commands (read-only)

```
status  stats  ver  clock  time  lifetime  radiostats  packetstats
telemetry  identity  location  nodes  neighbours  health  mailbox
power  powersaving  radio  rssi  acl  quiet  cb
set repeat  set advert.interval  set tx  set name
alert  ratelimit  sleep  rxboost  help
```

### Admin-only commands (read-write)

```
set name <X>  set lat <X>  set lon <X>
set repeat on/off  set flood.max <N>
set advert.interval <min>  set tx <dBm>  set tx auto on/off
password <pwd>  set guest.password <pwd>
powersaving on/off  mode 0/1/2
sleep on/off  rxboost on/off
advert  advert local  ping  ping <hash>  trace <hash>
alert on/off/dest/clear  mailbox clear
quiet <start> <end>  quiet off
ratelimit on/off/reset  clear stats  neighbor.remove <hex>
report on/off/dest/time/test/nodes
save  erase  reset  reboot
```

## Radio Settings (EU868 default)

| Parameter | Value |
|-----------|-------|
| Frequency | 869.618 MHz |
| Bandwidth | 62.5 kHz |
| Spreading Factor | SF8 |
| Coding Rate | 4/8 |
| TX Power | 14 dBm |
| Sync Word | 0x12 |

## Tips

1. Always `save` after changing configuration
2. Set passwords before deploying: `password myAdminPwd` and `set guest.password myGuestPwd`
3. Use `set lat` and `set lon` separately to set GPS coordinates
4. Use `set advert.interval 5` for 5-minute ADVERT interval
5. Use `set tx auto on` to enable adaptive TX power
6. Use `powersaving on` for maximum battery life (mode 2)
7. Use `health` to monitor mesh link quality and node availability
8. Enable `alert on` to get automatic notifications when nodes go offline
9. The `mailbox` stores messages for offline nodes automatically - no config needed
10. Use `tempradio` to test radio parameters without persisting, `set radio` to apply
