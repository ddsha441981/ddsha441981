# ⚡ Sketchboot — Fixed-Memory Spring Boot Rate Limiter via Java FFM & Rust

> **Off-Heap Count-Min Sketch Rate Limiting Starter for Spring Boot 3.x**

[![Java 22](https://img.shields.io/badge/Java-22-blue.svg)](https://www.oracle.com/java/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.x-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Maven Central](https://img.shields.io/badge/Maven%20Central-1.0.1-orange.svg)](https://search.maven.org)

Sketchboot is a Spring Boot 3.x auto-configuration starter providing fixed-memory rate limiting capabilities. Powered by Java 22 Foreign Function & Memory (FFM) API calls to native Rust `cl-tds` routines, Sketchboot executes lock-free rate checks without linear heap scaling or Redis network overhead.

---

## ⚡ Architectural Comparison (100 Million Operations)

| Metric | HashMap-based Limiters (Bucket4j) | Sketchboot Starter |
|---|---|---|
| **Data Structure** | `ConcurrentHashMap` | Off-Heap `AtomicU32` Array |
| **Heap Memory at 100M Keys** | ~15 GB+ (Heap risk) | **1 MB Fixed (Off-Heap)** |
| **Concurrency** | Synchronization locks | Lock-free Rust CAS |
| **Garbage Collection Pauses** | High GC churn | **Zero Java Heap Allocation** |

---

## 🛠️ Declarative Annotation Suite

Includes 7 domain-specific SpEL-backed annotations:

1. `@SketchLimit`: General request rate limiting.
2. `@SketchShield`: Brute-force authentication defense.
3. `@SketchFraud`: Financial & payment card transaction fraud gating.
4. `@SketchHitter`: High-frequency endpoint stream detection.
5. `@SketchSurge`: Webhook traffic spike containment.
6. `@SketchCheat`: Game action monitoring.
7. `@SketchSensor`: IoT sensor event burst suppression.

---

## 💻 Code Example

```java
@RestController
public class SecurityController {

    @SketchShield(threshold = 3, windowMs = 60000, key = "#ipAddress")
    @PostMapping("/login")
    public ResponseEntity<String> login(@RequestHeader("X-Forwarded-For") String ipAddress) {
        return ResponseEntity.ok("Authenticated");
    }
}
```

---

## 📜 License

Licensed under the Apache License, Version 2.0.
