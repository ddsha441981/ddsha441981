# 🩺 WireDoctor — Spring Boot Architectural & Runtime Dependency Graph Analyzer

> **Zero-Intrusion Runtime Diagnostics, Cycle Detection, and Architectural CI Gating for Spring Boot**

[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-2.7%20--%204.0.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Java Version](https://img.shields.io/badge/Java-17%20%7C%2021%20%7C%2025-blue.svg)](https://openjdk.org/)
[![Maven Central](https://img.shields.io/badge/Maven%20Central-0.9.0-orange.svg)](https://mvnrepository.com)

WireDoctor is a lightweight, zero-intrusion runtime diagnostic tool for Spring Boot applications. By hooking directly into the resolved `ApplicationContext` post-startup, WireDoctor constructs the exact bean dependency graph, identifies structural smells, measures instantiation latency via `BufferingApplicationStartup`, and enforces architectural performance gates in CI pipelines.

---

## ⚡ Core Technical Features

### 1. Startup Latency & Critical Path Analysis
- Leverages Spring's native `BufferingApplicationStartup` (Boot 2.4+) to extract exact, unreflected bean initialization timings.
- Computes the **Instantiation Critical Path** to isolate the exact chain of blocking bean dependencies delaying application readiness.

### 2. Resolved Dependency Graph & Cycle Resolution
- Reads directly from `getDependenciesForBean()` to capture true runtime wiring rather than static AST assumptions.
- Applies **Tarjan’s Strongly Connected Components (SCC)** algorithm to find hidden circular dependencies resolved silently by Spring proxies.
- Ranks `@Lazy` candidate injections by blast radius reduction to break cycles with minimal code modification.

### 3. Upgrade Guard & Autoconfiguration Diffing
- Captures Spring Boot condition evaluation snapshots (`ConditionEvaluationReport`).
- Diffing engine compares baseline configuration against current builds to detect quiet `matched → notMatched` flips across Spring Boot version upgrades.

### 4. Architectural CI Gating
- Generates `wiredoctor-baseline.json` lockfiles.
- Fails build pipelines on structural regressions (`fail-on=new-cycle`), startup timing regressions, or newly introduced slow beans.

---

## 📊 Compatibility Matrix

| Spring Boot Version | Java 17 | Java 21 | Java 25 | WebFlux / Reactive |
|---|:---:|:---:|:---:|:---:|
| **Boot 2.7.x** | ✅ | ✅ | ✅ | ✅ |
| **Boot 3.3.x** | ✅ | ✅ | ✅ | ✅ |
| **Boot 3.5.x** | ✅ | ✅ | ✅ | ✅ |
| **Boot 4.0.x** | ✅ | ✅ | ✅ | ✅ |

*Note: Requires JVM mode (Boot 2.4+ floor). GraalVM Native Image AOT processing is currently unsupported.*

---

## 🚀 Integration & Configuration

### Maven
```xml
<dependency>
    <groupId>io.github.ddsha441981</groupId>
    <artifactId>wiredoctor-autoconfigure</artifactId>
    <version>0.9.0</version>
</dependency>
```

### Gradle
```groovy
implementation 'io.github.ddsha441981:wiredoctor-autoconfigure:0.9.0'
```

### CI Gate Enforcement
```bash
# Capture architectural baseline lockfile
./mvnw spring-boot:run \
  -Dspring-boot.run.arguments="--wiredoctor.baseline=wiredoctor-baseline.json --wiredoctor.baseline-write=true"
```

```properties
# application-ci.properties
wiredoctor.baseline=wiredoctor-baseline.json
wiredoctor.fail-on=new-cycle,startup-time,slow-bean
```

---

## 📜 Artifact Outputs

- `wiredoctor-report.html`: Self-contained, offline interactive console (Graph, Ghosts, Smells, Timing, Conditions).
- `wiredoctor-report.json`: Structured machine-readable schema for programmatic audit pipelines.
- `wiredoctor-gate.status`: CI status verification payload (`PASS` / `FAIL`).

---

## 📜 License

Dual-licensed under MIT OR Apache-2.0.
