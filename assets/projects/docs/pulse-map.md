# ⚡ PulseMap — Fixed-Capacity Hash Table with LFU+LRU Eviction

> **Cache-Line Aligned, Zero-Heap Numeric Storage Eviction Cache in Pure Rust**

[![Crate](https://img.shields.io/crates/v/pulse_map.svg)](https://crates.io/crates/pulse_map)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-57%20passing-brightgreen)]()

PulseMap is a high-performance fixed-capacity hash table featuring hybrid LFU+LRU eviction logic. Unlike standard standard-library maps, PulseMap enforces hard memory bounds by evicting cold entries directly within 64-byte cache-line aligned bucket structures.

---

## 🔬 Architectural Engineering

### 64-Byte Cache-Line Aligned Bucket Layout
Each bucket occupies exactly 64 bytes (one CPU L3 cache line):

```
┌──────────────────────────────────────────────────────────────────┐
│                    ONE BUCKET (64 bytes)                         │
├──────────────────────────────────────────────────────────────────┤
│  MetaWord (8 B): 4×2b States | 4×7b H2 Fingerprints | 4×7b Priority│
│  Slot 0 (14 B) | Slot 1 (14 B) | Slot 2 (14 B) | Slot 3 (14 B)     │
└──────────────────────────────────────────────────────────────────┘
```

- **Inline Storage**: Primitive keys/values ($\le 6\text{B}$ key, $\le 7\text{B}$ value) are stored directly inside the bucket word without heap allocations.
- **Slab Pool Storage**: Larger allocations fall back to fixed slab pool indexing.
- **TTL Support**: Epoch-based TTL expiration without background eviction threads.

---

## 📊 Performance Benchmarks vs `lru` Crate

| Benchmark (100K ops) | PulseMap | `lru` crate | Result |
|---|:---:|:---:|:---:|
| **INSERT** | **13.8 ms** | 19.1 ms | **1.4x faster** |
| **MIXED (Insert + Lookup)** | **16.0 ms** | 23.7 ms | **1.5x faster** |
| **EVICTION (50K)** | **1.5 ms** | 2.2 ms | **1.5x faster** |

---

## 🌐 Multi-Language FFI Support

Includes native FFI bindings for:
- **C**: C-ABI standard library `pulse_map.h`.
- **Python**: PyO3 bindings (`pulse_map_py`).
- **Java**: Java 22+ Foreign Function & Memory (FFM) Panama bindings.
- **Node.js**: N-API native add-ons.

---

## 📜 License

Dual-licensed under MIT OR Apache-2.0.
