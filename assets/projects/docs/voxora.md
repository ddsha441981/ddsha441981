# 🎙️ Voxora Service — Systems Audio Capture & Multi-Language Transcription Daemon

> **High-Performance Rust Service Daemon for Real-Time Audio Stream Processing and Keyring-Secured LLM Integrations**

[![Rust Service](https://img.shields.io/badge/Service-Rust%20Systemd-orange.svg)](https://www.rust-lang.org)
[![Deepgram](https://img.shields.io/badge/Engine-Deepgram%20Nova--3-0052CC.svg)](https://deepgram.com)
[![Linux Keyring](https://img.shields.io/badge/Security-Freedesktop%20SecretService-brightgreen.svg)](#)

Voxora Service is an enterprise Linux audio processing daemon written in Rust. It captures system and speaker audio (`SpeakerCapture`) in real-time, routes linear PCM streams into dual-language Deepgram transcription servers (English/Hindi), and interfaces securely with local and remote LLM providers via Linux SecretService keyrings.

---

## ⚡ System Architecture & Components

```
┌─────────────────┐     PCM Stream     ┌────────────────────────┐
│ SpeakerCapture  │ ─────────────────> │ Deepgram Go-Server     │
│ (Linux Audio)   │                    │ (Nova-3 EN / HI models)│
└─────────────────┘                    └───────────┬────────────┘
                                                   │ Websockets
                                                   ▼
┌───────────────────────────────────────────────────────────────┐
│ Voxora Service Daemon (Rust, Port 8080)                       │
│ • Systemd User / System Service Lifecycle                     │
│ • Keyring Secret Store (org.freedesktop.secrets)             │
│ • AnythingLLM Vector Workspace Integration                    │
└───────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Key Features

- **Multi-Language Audio Routing**: Concurrent streaming pipelines for `en-US` and `hi` Nova-3 models over zero-copy IPC log queues.
- **Freedesktop SecretService Security**: Secure API key storage via GNOME Keyring (`libsecret`), avoiding plaintext environment variables.
- **Systemd Process Lifecycle**: Configured for both `systemctl --user` and root-level systemd service auto-recovery.
- **AnythingLLM Integration**: Built-in HTTP gateway for direct vector search and RAG querying.

---

## 🚀 Service Operations

```bash
# User service status
systemctl --user status voxora

# Follow live service logs
journalctl --user -u voxora -f
```

---

## 📜 License

Proprietary / Internal Systems Utility.
