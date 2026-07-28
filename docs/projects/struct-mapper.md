# 🔄 struct-mapper — Zero-Boilerplate Rust Struct Conversion Macro

> **Procedural Derive Macro for `From<T>` and `TryFrom<T>` Code Generation**

[![Crates.io](https://img.shields.io/badge/crates.io-v0.2.0-orange?style=flat-square&logo=rust)](https://crates.io/crates/struct-mapper)
[![Docs](https://img.shields.io/badge/docs.rs-struct--mapper-blue?style=flat-square&logo=docs.rs)](https://docs.rs/struct-mapper)
[![License](https://img.shields.io/badge/license-MIT%2FApache--2.0-green?style=flat-square)](LICENSE)

`struct-mapper` is a procedural macro library that auto-generates zero-overhead `From<Source>` and `TryFrom<Source>` implementations at compile time.

---

## ⚡ Key Macro Attributes

| Attribute | Scope | Functional Behavior |
|---|---|---|
| `#[map_from(Type)]` | Struct | Generates `impl From<Type>` |
| `#[try_map_from(Type)]` | Struct | Generates `impl TryFrom<Type>` |
| `#[map(from = "field")]` | Field | Maps from differently named source field |
| `#[map(skip, default)]` | Field | Skips source mapping, populates `Default::default()` |
| `#[map(into)]` | Field | Calls `.into()` on nested struct field |
| `#[map(with = "func")]` | Field | Executes custom transformation function |
| `#[map(try_into)]` | Field | Calls `.try_into()` for fallible field conversions |

---

## 💻 Rust Usage Example

```rust
use struct_mapper::MapFrom;

struct UserEntity {
    name: String,
    age: u32,
}

#[derive(MapFrom)]
#[map_from(UserEntity)]
struct UserResponse {
    name: String,
    age: u32,
    #[map(skip, default)]
    request_id: String,
}

let entity = UserEntity { name: "Alice".into(), age: 30 };
let response: UserResponse = entity.into();
```

---

## 📜 License

Dual-licensed under MIT OR Apache-2.0.
