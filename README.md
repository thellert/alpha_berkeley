# Alpha Berkeley Framework


> **🚧 Early Access Release**  
> This is an early access version of the Alpha Berkeley Framework. While the core functionality is stable and ready for experimentation, documentation and APIs may still evolve. We welcome feedback and contributions!

An open-source, domain-agnostic, capability-based architecture for building intelligent agents that can be adapted to any specific domain.

**📢 Conference Update**  
Our work "Agentic Systems in Accelerator Control and Optimization" will be presented as a contributed **oral presentation** at [ICALEPCS'25](https://indico.jacow.org/event/86/overview).

**🎉 Latest Release: v0.7.1** - Major architecture update! Framework is now pip-installable, enabling independent application development. See [Release Notes](RELEASE_NOTES.md) for details.

## 🚀 Quick Start

```bash
# Install the framework
pip install alpha-berkeley-framework

# Create a new project from a template
framework init my-weather-agent --template hello_world_weather

# Navigate to your project
cd my-weather-agent

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start the command line chat interface
framework chat

# Or use the web interface at http://localhost:8080
```

## 📚 Documentation

**[📖 Read the Full Documentation →](https://thellert.github.io/alpha_berkeley)**

## Quick Links

- **[🚀 Getting Started](https://thellert.github.io/alpha_berkeley/getting-started/)** - Complete learning path from setup to building sophisticated agents
- **[📖 Installation Guide](https://thellert.github.io/alpha_berkeley/getting-started/installation)** - Fresh installation instructions
- **[🔄 Migration Guide](https://thellert.github.io/alpha_berkeley/getting-started/migration-guide)** - Upgrading from v0.6.x to v0.7.0
- **[🎓 Tutorials](https://thellert.github.io/alpha_berkeley/getting-started/)** - Step-by-step guides for building agents
- **[📝 Release Notes](RELEASE_NOTES.md)** - What's new in v0.7.0
- **[📋 Issue #8](https://github.com/thellert/alpha_berkeley/issues/8)** - Framework decoupling architecture

## ✨ What's New in v0.7.0

**Major Architecture Update** - Framework decoupled from applications:

- 🎯 **Independent Development** - Applications in separate repositories
- 📦 **Pip-Installable** - `pip install alpha-berkeley-framework`
- 🛠️ **Unified CLI** - 5 commands (`init`, `deploy`, `chat`, `health`, `export-config`)
- 📋 **Template System** - Generate complete projects instantly
- 🎨 **Registry Helpers** - ~70% less boilerplate code
- ⚡ **Immediate Changes** - Edit code, run instantly (no reinstall)

**Breaking Changes:** v0.7.0 changes import paths and configuration structure. See [Migration Guide](https://thellert.github.io/alpha_berkeley/getting-started/migration-guide) for upgrade instructions.

## Key Features

- **Scalable Capability Management** - Efficiently scales to large sets of specialized agents
- **Structured Orchestration** - Converts freeform inputs into clear, executable plans
- **Modular Architecture** - Easily integrates new capabilities without disrupting workflows
- **Human-in-the-Loop Ready** - Transparent execution plans for inspection and debugging
- **Domain-Adaptable** - Designed for heterogeneous scientific infrastructure

---

## 📖 Citation

If you use the Alpha Berkeley Framework in your research or projects, please cite our [paper](https://arxiv.org/abs/2508.15066):

```bibtex
@misc{hellert2025alphaberkeley,
      title={Alpha Berkeley: A Scalable Framework for the Orchestration of Agentic Systems}, 
      author={Thorsten Hellert and João Montenegro and Antonin Sulc},
      year={2025},
      eprint={2508.15066},
      archivePrefix={arXiv},
      primaryClass={cs.MA},
      url={https://arxiv.org/abs/2508.15066}, 
}
```

---

*For detailed installation instructions, tutorials, and API reference, please visit our [complete documentation](https://thellert.github.io/alpha_berkeley).*

---

**Copyright Notice**

Alpha Berkeley Framework (alpha berkeley) Copyright (c) 2025, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

If you have questions about your rights to use or distribute this software,
please contact Berkeley Lab's Intellectual Property Office at
IPO@lbl.gov.

NOTICE.  This Software was developed under funding from the U.S. Department
of Energy and the U.S. Government consequently retains certain rights.  As
such, the U.S. Government has been granted for itself and others acting on
its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the
Software to reproduce, distribute copies to the public, prepare derivative 
works, and perform publicly and display publicly, and to permit others to do so.

---