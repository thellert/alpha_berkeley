# Osprey Framework

> **🦅 Rebranded from Alpha Berkeley Framework**  
> This project has been renamed to Osprey Framework. If you're upgrading from the Alpha Berkeley Framework, see the [migration guide](https://als-apg.github.io/osprey/getting-started/migration-guide.html).

> **🚧 Early Access Release**  
> This is an early access version of the Osprey Framework. While the core functionality is stable and ready for experimentation, documentation and APIs may still evolve. We welcome feedback and contributions!

An open-source, domain-agnostic, capability-based architecture for building intelligent agents that can be adapted to any specific domain.

**📄 Research**  
This work was presented as a contributed oral presentation at [ICALEPCS'25](https://indico.jacow.org/event/86/overview) and will be featured at the [Machine Learning and the Physical Sciences Workshop](https://ml4physicalsciences.github.io/2025/) at NeurIPS 2025.


## 🚀 Quick Start

```bash
# Install the framework
pip install osprey-framework

# Create a new project from a template
osprey init my-weather-agent --template hello_world_weather

# Navigate to your project
cd my-weather-agent

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Start the command line chat interface
osprey chat

# Or use the web interface at http://localhost:8080
```


## 📚 Documentation

**[📖 Read the Full Documentation →](https://als-apg.github.io/osprey)**


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

*For detailed installation instructions, tutorials, and API reference, please visit our [complete documentation](https://als-apg.github.io/osprey).*

---

**Copyright Notice**

Osprey Framework Copyright (c) 2025, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved.

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