# CubeCellMeshCore v0.7.0

Firmware par repeater MeshCore par el Heltec CubeCell HTCC-AB01.

## Cossa ghe xe de novo ne la v0.7.0

- **Statistiche Link Quality Miorae** - Medie mobili esponensiali (EMA) de RSSI/SNR par ogni visìn
  - Nove metriche: `rssiAvg`, `snrAvg`, `pktCount`, `pktCountWindow`
  - Finestre de misurassion de 60 secondi par calcolar el packet rate
  - Comando `neighbours` el mostra valori corenti e medi
  - Base par futuri algoritmi de routing inteligenti
- **Potensa TX Adativa** - Regolassion automatica de la potensa de trasmission
  - SNR > +10dB → Riduce potensa de 2 dBm (risparmio energia)
  - SNR < -5dB → Aumenta potensa de 2 dBm (mior copertura)
  - Range: 5-21 dBm con step de 2 dBm
  - Comandi: `set tx auto on/off`, `txpower auto on/off`, `txpower <5-21>`
- **Deduplicassion Pacheti** - Documentà cache ring-buffer a 32 slot
  - Previen inoltro de pacheti duplicai
  - Riduce congestione de la rete e previen loop
- **Suite de Test** - Novo script de verifica `tools/test_adaptive_tx.py`

## Funzionalità Precedenti (v0.5.0-v0.6.0)

- **Routing DIRECT** - Suporto completo par pacheti co rotta DIRECT (path peeling)
- **Casseta de Posta (Mailbox)** - 2 posti EEPROM + 4 in RAM
- **Dashboard Salute** - Comando `health` co vitali e nodi problematici
- **Configurassion Remota** - 50+ comandi CLI via canal cifra'
- **Sistema Loop Detection** - Modi configurabili: off, minimal, moderate, strict
- **Filtro Max Hops** - Auto-add contati limitai par hop count
- **Quiet Hours** - Rate limiting noturno par risparmiar bateria
- **Circuit Breaker** - Bloca DIRECT forwarding a visìn degradai

## Caratteristiche

- Compatibile col protocollo MeshCore (app Android/iOS)
- Identita' e firme Ed25519
- Broadcasting ADVERT co sincronizassion del tempo
- Forwarding pacchetti con CSMA/CA basado sul SNR
- Casseta de posta par nodi offline (store-and-forward)
- Monitor de la salute de la rete con alerte automatiche
- Configurassion remota completa tramite CLI cifra'
- Report giornaliero automatico a l'admin
- Deep sleep (~20 uA de consumo)
- Telemetria bateria e temperatura
- Tracking dei visini (repeater direti a 0-hop)
- Rate limiting (login, richieste, forward)
- Statistiche persistenti in EEPROM

## Hardware

- **Scheda**: Heltec CubeCell HTCC-AB01
- **MCU**: ASR6501 (ARM Cortex-M0+ @ 48 MHz + SX1262)
- **Flash**: 128 KB (91.0% doparadi, ~12 KB libari)
- **RAM**: 16 KB (47.9% doparadi)
- **Radio**: SX1262 LoRa (EU868: 869.618 MHz, BW 62.5 kHz, SF8, CR 4/8)

## File nel pacchetto

| File | Descrission |
|------|-------------|
| `firmware.cyacd` | Imagine Flash par CubeCellTool (Windows) |
| `firmware.hex` | Formato Intel HEX |
| `INSTALL.md` | Guida de instalassion e primo avvio |
| `COMMANDS.md` | Riferimento comandi completo (50+ comandi) |
| `README.md` | Versione inglese |
| `README_VEN.md` | Sta pàgina qua |

## Come partire

1. Flasha `firmware.cyacd` co CubeCellTool o PlatformIO
2. Colegate la seriale a 115200 baud
3. Meti le password: `passwd admin <pwd>` e dopo `save`
4. Meti el nome: `name ElMeRepeater` e dopo `save`
5. El nodo el scominsia a mandar ADVERT e a inoltrare pacchetti

Varda `INSTALL.md` par le istrussioni detajae.

## Autor

**Andrea Bernardi** - Creador del projeto e svilupador prinsipal

## Link

- Sorgenti: https://github.com/atomozero/CubeCellMeshCore
- MeshCore: https://github.com/meshcore-dev/MeshCore

## Licensa

Licensa MIT - Varda el file LICENSE par i detagli.

---
*Fato col cuor a Venessia* 🦁
