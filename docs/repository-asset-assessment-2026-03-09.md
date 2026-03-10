# ALOHA-Lite Repository — Coding Asset Assessment Report

**Prepared for:** Board of Directors
**Assessment Date:** 2026-03-09
**Repository:** github.com/hafnium49/aloha-lite (Public)
**Assessor:** Independent automated code audit

---

## Executive Summary

ALOHA-Lite is a robotics software platform for bilateral teleoperation and autonomous manipulation, combining FastAPI microservices, computer vision (SAM2), and ML-driven color optimization. The codebase represents approximately **4 months of active development** (July–October 2025) by a **single developer**, totaling **435 commits** and **~227,000 lines of code** across 654 tracked files. The project demonstrates meaningful domain-specific innovation in robot control and ML-integrated color calibration. However, as a corporate asset, the repository carries **significant governance, quality assurance, and operational maturity gaps** that materially affect its defensibility, maintainability, and scalability.

**Overall Maturity Rating: Early-Stage Prototype / Research**

---

## 1. Repository Vital Statistics

| Metric | Value |
|---|---|
| Created | 2025-07-03 |
| Last Commit | 2025-10-29 |
| Active Development Period | 118 days |
| Total Commits (all branches) | 435 (412 non-merge, 23 merge) |
| Tracked Files | 654 |
| Total Lines of Code | ~227,000 |
| Repository Size (disk) | 47 MB working tree, 17 MB git objects |
| GitHub Disk Usage | 16.2 MB |
| Primary Language | Python (2.56 MB / 68,763 lines) |
| Secondary Languages | TypeScript (500 KB / 15,451 lines), Shell, HTML, CSS |
| Stars / Forks / Watchers | 0 / 0 / 0 |
| Visibility | **Public** |
| License | **None** |

---

## 2. Contributor Analysis

### 2.1 Bus Factor: Critical Risk — Score 1

All 435 commits originate from a **single individual** (Hiroki Fujiwara) operating under 4 different git identities:

| Identity | Commits | Email |
|---|---|---|
| hafnium | 326 | hafnium49@gmail.com |
| Hiroki Fujiwara | 80 | hafnium49@gmail.com |
| hafnium49 | 28 | hafnium49@gmail.com |
| root | 1 | root@alohalite.localdomain |

**Key Risks:**
- Complete single-point-of-failure for all institutional knowledge
- The use of personal email (gmail.com) rather than a corporate domain raises IP assignment questions
- One commit was made as `root` on a local machine — suggests occasional development directly on robot hardware without proper user isolation

### 2.2 AI-Assisted Development Pattern

All 13 pull requests carry the **"codex"** label, and 12 of the 15 remote branches follow the naming convention `codex/<task-description>`, indicating systematic use of **GitHub Codex / AI coding agents** for feature development. This is a modern practice but raises questions about code comprehension depth by the human developer.

---

## 3. Development Process Assessment

### 3.1 Version Control Practices

| Practice | Status | Risk Level |
|---|---|---|
| Branch strategy | Feature branches via codex → main | Low |
| Branch cleanup | All 15 remote branches merged to main | OK |
| Tags / Releases | **None** | High |
| Semantic versioning | **Not implemented** | High |
| Commit signing | **Not configured** | Medium |

**Commit Message Quality:**
- 148 of 435 commits (34%) follow conventional commit format (`feat:`, `fix:`, `chore:`, etc.)
- Remaining 66% use inconsistent formats including generic messages like *"Implement feature X to enhance user experience and optimize performance"* (appears verbatim in multiple commits — auto-generated placeholder)
- Some commit messages are excessively long (100+ chars in title line)

### 3.2 Code Review Process — **Non-Existent**

| Metric | Value |
|---|---|
| Total Pull Requests | 13 (all merged) |
| PRs with inline comments | 0 of 13 |
| PRs with reviews | 0 of 13 |
| Average time to merge | **3 minutes** |
| Fastest merge | **0 minutes** (7 PRs merged instantly) |
| Longest merge | 31 minutes |

**Critical Finding:** No pull request in the repository's history has ever received a human code review. All PRs were self-merged by the sole contributor within seconds to minutes. This represents a **complete absence of quality gates** and peer review.

### 3.3 CI/CD Pipeline — **Non-Existent**

| Component | Status |
|---|---|
| GitHub Actions workflows | 0 configured |
| Branch protection rules | None |
| Automated testing on PR | None |
| Deployment automation | None |
| Code quality gates | None |

The repository has a `docker-compose.yml` for local orchestration but no automated build, test, or deployment pipeline.

### 3.4 Issue Tracking — **Not Used**

- Total GitHub Issues: **0** (open or closed)
- No evidence of formal bug tracking, feature requests, or task management

---

## 4. Codebase Architecture & Quality

### 4.1 Project Structure

```
aloha-lite/
├── frontend/          # FastAPI ML service + HTML/CSS frontend
├── robot_service/     # Robot hardware control service
├── vision_bridge/     # SAM2 computer vision service
├── mcp_server/        # Model Context Protocol server
├── so101_mcp_server/  # SO-101 robot MCP server
├── utilities/         # Calibration, trajectory planning tools
├── phosphobot/        # Vendored third-party library (subtree)
├── aloha-lite-demo2rule/ # Demo-to-rule conversion
├── temp_rules/        # Robot procedure configurations (JSON)
├── tests/             # Top-level integration tests
├── scripts/           # Utility scripts
└── examples/          # Usage examples
```

### 4.2 Language Distribution (Lines of Code)

| Language | Lines | Purpose |
|---|---|---|
| Python | 68,763 | Core services, ML, robot control |
| Markdown | 19,474 | Documentation (74 files) |
| TypeScript/TSX | 15,451 | Frontend components |
| JSON | 11,960 | Robot configs, procedures |
| Shell | 1,087 | Setup & utility scripts |

### 4.3 Code Hotspots (Most Frequently Modified Files)

| File | Modifications | Concern |
|---|---|---|
| `temp_rules/robot_configurations.json` | 69 | Excessive churn on config |
| `frontend/main.py` | 60 | Core service instability |
| `frontend/index.html` | 29 | Frequent UI rework |
| `README.md` | 28 | Documentation churn |
| `.gitignore` | 27 | Repeated oversight |
| `robot_service/main.py` | 25 | Core service instability |

The high modification count on core files (60+ edits to `frontend/main.py`) suggests iterative trial-and-error development rather than planned architecture.

### 4.4 Test Coverage

| Metric | Value |
|---|---|
| Test files | 68 |
| Production Python files | 151 |
| Test-to-production ratio | 0.45 |
| pytest configured | Yes (pyproject.toml) |
| CI test execution | **None** |
| Coverage reporting | Configured but not automated |
| conftest.py files | **0** (no shared test fixtures) |

Tests exist in quantity but there is **no evidence they are routinely executed** as part of any automated process. Without CI, test rot is likely.

### 4.5 Repository Hygiene Issues

| Issue | Details | Severity |
|---|---|---|
| **Committed artifact file** | `=2.0.0` — pip install output accidentally committed as a file | Medium |
| **Large binary files** | URDF mesh files (STL/DAE) up to 6 MB each committed directly | Medium |
| **Committed error log** | `error_log.md` (72 KB) tracked in version control | Low |
| **Vendored subtree** | `phosphobot/` (~30 MB) included as git subtree | Medium |
| **No .dockerignore** | Potential for bloated Docker images | Low |

---

## 5. Intellectual Property & Legal

### 5.1 License — **CRITICAL GAP**

The repository has **no LICENSE file** and GitHub reports `licenseInfo: null`. For a **public repository**, this means:

- Default copyright applies (all rights reserved by the author)
- Third parties have **no explicit permission** to use, modify, or distribute the code
- However, being public on GitHub grants implicit permission to view and fork under GitHub's Terms of Service
- The lack of a formal license creates **legal ambiguity** for both the company and any downstream users

### 5.2 IP Ownership Concerns

- All commits use a **personal Gmail address** (hafnium49@gmail.com), not a corporate email
- No Contributor License Agreement (CLA) or IP assignment documentation evident
- Significant use of AI code generation (Codex) — IP ownership of AI-generated code varies by jurisdiction
- Vendored `phosphobot` library likely carries its own license terms (not audited)

### 5.3 Dependency Risk

Dependencies declared in `requirements.txt` and `pyproject.toml` — no license audit of third-party dependencies has been performed (no tool like `pip-licenses` configured).

---

## 6. Security Assessment

| Area | Status | Risk |
|---|---|---|
| Secrets in repository | `.env.example` provided (good); no `.env` committed | Low |
| Branch protection | **None** — anyone with push access can force-push to main | **High** |
| Dependency scanning | **None** — no Dependabot, Snyk, or similar | **High** |
| SAST (static analysis) | **None** | Medium |
| Authentication tokens | Documented as env vars; service-to-service auth present | Acceptable |
| Commit signing | Not enforced | Medium |

---

## 7. Development Activity & Momentum

### 7.1 Commit Timeline

| Period | Commits | Activity Level |
|---|---|---|
| 2025-W27 (Jul 1-6) | 10 | Project inception |
| 2025-W28 (Jul 7-13) | 10 | Low |
| 2025-W29 (Jul 14-20) | 98 | **Peak sprint** |
| 2025-W30 (Jul 21-27) | 114 | **Peak sprint** |
| 2025-W31 (Jul 28-Aug 3) | 137 | **Peak sprint** |
| 2025-W32 (Aug 4-10) | 54 | Declining |
| 2025-W38 (Sep 15-21) | 10 | Sporadic |
| 2025-W43 (Oct 20-26) | 1 | Near-dormant |
| 2025-W44 (Oct 27-Nov 2) | 1 | Near-dormant |
| Nov 2025 – Mar 2026 | 0 | **Dormant** |

**Finding:** 94% of all commits occurred in a single 5-week burst (mid-July to early August 2025). The repository has been **effectively dormant for over 4 months** with no commits since October 2025.

### 7.2 Monthly Breakdown

| Month | Commits |
|---|---|
| July 2025 | 305 |
| August 2025 | 118 |
| September 2025 | 10 |
| October 2025 | 2 |

---

## 8. Documentation

**Strength:** The project has extensive documentation with 74 markdown files totaling ~19,500 lines, including:
- Architecture details (`ARCHITECTURE_DETAILS.md`)
- Codebase overview (`CODEBASE_OVERVIEW.md`)
- Quick reference guide (`QUICK_REFERENCE.md`)
- Documentation index (`DOCUMENTATION_INDEX.md`)
- Per-module README files
- CLAUDE.md for AI assistant guidance

**Weakness:** Documentation volume appears disproportionate to code maturity, and much appears AI-generated. No versioned API documentation (e.g., OpenAPI/Swagger export) is maintained separately.

---

## 9. Risk Matrix Summary

| Risk Category | Severity | Impact | Mitigation Urgency |
|---|---|---|---|
| Bus factor of 1 | **Critical** | Total knowledge loss if developer unavailable | Immediate |
| No code review process | **Critical** | Undetected bugs, security vulnerabilities | Immediate |
| No CI/CD pipeline | **High** | No automated quality gates | High |
| No license | **High** | Legal exposure on public repository | Immediate |
| Repository dormant 4+ months | **High** | Potential project abandonment | High |
| No dependency scanning | **High** | Supply chain vulnerabilities | High |
| IP ownership ambiguity | **High** | Contested ownership claims | Immediate |
| No branch protection | **Medium** | Accidental/malicious main branch corruption | Medium |
| No release versioning | **Medium** | No deployable snapshots | Medium |
| Large binaries in git | **Medium** | Repository bloat over time | Low |
| Committed artifacts | **Low** | Clutter | Low |

---

## 10. Valuation Considerations

### Strengths as an Asset
1. **Domain-specific innovation** — Combines robotics, ML optimization, and vision processing in a coherent architecture
2. **Microservice architecture** — Clean separation into 5 services with Docker orchestration
3. **Configuration-driven design** — Robot movements defined in JSON, enabling non-programmer operation
4. **MCP integration** — Forward-looking LLM integration via Model Context Protocol
5. **Extensive documentation** — Comprehensive guides for onboarding
6. **Test infrastructure** — 68 test files with pytest configuration

### Weaknesses as an Asset
1. **Single-developer dependency** — No knowledge transfer, no cross-training
2. **Zero process maturity** — No reviews, no CI, no issue tracking, no releases
3. **Dormant status** — No meaningful development in 4+ months
4. **Legal gaps** — No license, personal email commits, AI-generated code IP questions
5. **No production evidence** — No deployment pipeline, no monitoring, no release history
6. **Public exposure** — Source code publicly visible without clear licensing terms

---

## 11. Domain-Specific Technology Stack

An audit of dependency files (`requirements.txt`, `pyproject.toml`, `package.json`) and import statements across **all 16 branches** (local and remote) reveals the following specialized modules. Standard Python libraries and common data science packages (numpy, pandas, etc.) are excluded.

### 11.1 Robotics & Hardware Control

| Module | Purpose | Location | Version |
|---|---|---|---|
| **dynamixel-sdk** | Dynamixel servo motor communication | `phosphobot/` | v3.7.31+ |
| **feetech-servo-sdk** | Feetech servo motor communication | `phosphobot/` | v1.0.0+ |
| **modern-robotics** | Screw-theory trajectory planning | `robot_service/`, `utilities/` | v1.0.0+ |
| **pybullet** | Physics simulation environment | `phosphobot/` | v3.2.7+ |
| **pyrealsense2** | Intel RealSense depth camera driver | `phosphobot/` | v2.54+ |
| **go2-webrtc-driver** | Unitree Go2 robot dog WebRTC control | `phosphobot/` | v0.2.0+ |

### 11.2 AI / Deep Learning

| Module | Purpose | Location | Version |
|---|---|---|---|
| **torch** (PyTorch) | Neural network inference engine | `vision_bridge/`, `phosphobot/modal/` | v2.5.1+ / v2.7.0+ |
| **torchvision** | Vision model utilities | `vision_bridge/`, `phosphobot/modal/` | v0.20.1+ / v0.22.0+ |
| **transformers** | HuggingFace model loading (PaliGemma VLM) | `phosphobot/modal/` | v4.52.4+ |
| **lerobot** | Robot learning policies (ACT architecture) | `phosphobot/inference/ACT/` | — |
| **gr00t** (NVIDIA Isaac GR00T) | Foundation model for robot policy inference | `phosphobot/inference/gr00t/` | — |
| **einops** | Tensor rearrangement for ML pipelines | `phosphobot/modal/`, `phosphobot/scripts/` | v0.8.1+ |

### 11.3 Computer Vision

| Module | Purpose | Location | Version |
|---|---|---|---|
| **sam2** (Segment Anything 2) | Object segmentation with point prompts | `vision_bridge/` | — |
| **opencv-python** | Image processing and color space conversion | `vision_bridge/`, `phosphobot/` | v4.0+ / v4.5.0+ |
| **colour-checker-detection** | Color calibration chart detection | `vision_bridge/` | — |
| **colour** | Color science library (CIELAB transformations) | `frontend/` | — |

### 11.4 ML Optimization

| Module | Purpose | Location | Version |
|---|---|---|---|
| **scikit-learn** | Gaussian Process surrogate model for Bayesian optimization | `frontend/`, `vision_bridge/` | v1.0.0+ |
| **scipy** | Acquisition functions and numerical optimization | `frontend/` | v1.7.0+ |

### 11.5 Dataset & Model Management

| Module | Purpose | Location | Version |
|---|---|---|---|
| **huggingface-hub** | Model download/upload from HuggingFace Hub | `phosphobot/inference/`, `phosphobot/modal/` | v0.28.0+ |
| **datasets** | HuggingFace dataset handling for LeRobot | `phosphobot/` | v3.2.0+ |

### 11.6 Distributed Systems & Monitoring

| Module | Purpose | Location | Version |
|---|---|---|---|
| **pyzmq** (ZeroMQ) | Inter-process messaging for robot control | `robot_service/` | v26.* |
| **prometheus-client** | Metrics collection and monitoring endpoints | `robot_service/`, `vision_bridge/` | v0.20.* |
| **websockets** | MCP server bidirectional communication | `mcp_server/` | v10.0+ |

### 11.7 Cloud, Analytics & Observability (via phosphobot)

| Module | Purpose | Location | Version |
|---|---|---|---|
| **boto3** | AWS S3 storage for vision artifacts | `vision_bridge/` | — |
| **supabase** | Database backend | `phosphobot/` | v2.15.0+ |
| **sentry-sdk** | Error tracking and crash reporting | `phosphobot/` | v2.20.0+ |
| **posthog** | Product analytics telemetry | `phosphobot/` | v6.0.0+ |

### 11.8 Notable Absences

The following commonly expected robotics frameworks are **not used** in this project:

| Framework | Status | Alternative Used |
|---|---|---|
| NVIDIA Isaac Sim | Not present (only `gr00t` inference) | pybullet for simulation |
| MuJoCo / dm_control | Not present | pybullet for physics |
| ROS / ROS2 | Not present | Custom FastAPI microservices |
| TensorFlow | Not present | PyTorch-only stack |
| Gazebo | Not present | pybullet for simulation |

### 11.9 Dependency Consistency Across Branches

Dependencies are **uniform across all 16 branches** — no branch introduces unique dependencies not already present in `main`. The `phosphobot/` vendored subtree is the single largest source of external dependencies, carrying the deep learning inference stack (lerobot, gr00t, transformers) and hardware drivers (dynamixel, feetech, realsense).

**Total unique domain-specific modules: 27**

---

## 13. Recommendations

### Immediate (0-30 days)
1. **Add a LICENSE file** — Choose appropriate license (proprietary or open-source) and add immediately
2. **Establish IP assignment** — Execute formal IP assignment agreement with the developer; document corporate email for commits
3. **Enable branch protection** — Require PR reviews before merge to main
4. **Make repository private** (if proprietary) — Until licensing is resolved, public exposure is a liability
5. **Conduct security audit** — Run dependency vulnerability scan and SAST analysis

### Short-term (30-90 days)
6. **Implement CI/CD** — GitHub Actions for automated testing, linting, and security scanning
7. **Create first tagged release** — Establish versioning baseline
8. **Onboard second developer** — Reduce bus factor; enable code review
9. **Clean repository** — Remove committed artifacts (`=2.0.0`, `error_log.md`), migrate large binaries to Git LFS
10. **Audit third-party dependencies** — License compatibility and vulnerability review

### Medium-term (90-180 days)
11. **Establish formal development process** — Issue tracking, sprint planning, review requirements
12. **Implement monitoring and observability** — Production readiness
13. **Create deployment pipeline** — Automated staging and production deployment
14. **Document API contracts** — OpenAPI specs for inter-service communication

---

*End of Assessment*
