# Action Items: Google ADK Agent Starter Kit

**Date:** April 21, 2025  
**Author:** [Your Name], CTO  
**Based on:** Code Review Report (April 21, 2025)

## Overview

This document outlines the action items derived from the code review of our Google ADK Agent Starter Kit. These tasks are prioritized based on severity, impact on functionality, and alignment with our development roadmap.

## Task Tracking

| ID | Priority | Task | Owner | Status | Due Date | Dependencies |
|----|----------|------|-------|--------|----------|--------------|
| AI-001 | Critical | Fix Vertex AI Deployment Mechanism | CTO | Completed | May 1, 2025 | None |
| AI-002 | Medium | Improve CLI Extensibility | CTO | Completed | May 8, 2025 | None |
| AI-003 | Medium | Refactor Local Deployment UI | CTO | Completed | May 8, 2025 | None |
| AI-004 | Low | Align Testing Framework with Standards | CTO | Completed | May 15, 2025 | None |
| AI-005 | Low | Review Pydantic Usage | CTO | Completed | May 15, 2025 | None |
| AI-006 | High | Implement Vertex AI Agent Engine Deployment | CTO | Completed | May 5, 2025 | AI-001 |

## Detailed Task Descriptions

### AI-001: Fix Vertex AI Deployment Mechanism

**Priority:** Critical  
**Owner:** CTO  
**Due Date:** May 1, 2025  
**Status:** Completed

**Description:**  
The current Vertex AI deployment implementation incorrectly instantiates a generic `Agent` instead of our custom `SearchAgent` and fails to properly package tools. This renders the deployment functionality non-operational.

**Steps:**
1. Completely redesign the `prepare_deployment_package` function in `src/deployment/vertex.py`
2. Ensure our custom agent classes are included in the deployment package
3. Generate a `main.py` that correctly imports and instantiates our `SearchAgent` class
4. Implement proper packaging and instantiation of tools within the Vertex AI environment
5. Ensure proper serialization of tool objects rather than just their class names
6. Add comprehensive error handling and logging

**Success Criteria:**
- Successful deployment of our custom agent to Vertex AI
- Verification that the deployed agent uses our custom `SearchAgent` class
- Confirmation that all tools are properly packaged and functional
- End-to-end testing with sample queries

**Resources:**
- [Vertex AI Custom Container Documentation](https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements)
- [Google ADK Deployment Guide](https://cloud.google.com/vertex-ai/docs/agent-development-kit/deployment)

---

### AI-002: Improve CLI Extensibility

**Priority:** Medium  
**Owner:** CTO  
**Due Date:** May 8, 2025  
**Status:** Completed

**Description:**  
The CLI is hardcoded to support only the "search" agent type, limiting our ability to add new agent types without modifying the CLI code directly.

**Steps:**
1. Design an agent registry pattern that maps agent types to their implementation classes
2. Implement the registry in a new module (e.g., `src/registry.py`)
3. Update `src/cli.py` to use this registry for creating and running agents
4. Add a mechanism for dynamically registering new agent types
5. Update documentation to reflect the new extensibility pattern
6. Add unit tests for the registry functionality

**Success Criteria:**
- Ability to add new agent types without modifying the CLI code
- Successful registration and execution of at least one new agent type
- Comprehensive test coverage for the registry functionality
- Updated documentation with examples of adding new agent types

**Resources:**
- [Python Registry Pattern Examples](https://python-patterns.guide/registry/)
- [Click Documentation](https://click.palletsprojects.com/) (if we decide to migrate to Click)

---

### AI-003: Refactor Local Deployment UI

**Priority:** Medium  
**Owner:** CTO  
**Due Date:** May 8, 2025  
**Status:** Completed

**Description:**  
The current local deployment implementation generates HTML on the fly, coupling Python code with UI structure. This makes UI maintenance difficult and violates separation of concerns.

**Steps:**
1. Create a proper `templates` directory with static HTML files
2. Move the existing HTML template to a static file
3. Update `src/deployment/local.py` to use Jinja2 templates properly
4. Separate UI concerns from backend logic
5. Add CSS and JavaScript as separate files in a `static` directory
6. Implement proper error handling and user feedback
7. Add responsive design elements for better mobile support

**Success Criteria:**
- Clean separation of UI and backend code
- Improved maintainability of the UI components
- Proper use of Jinja2 templates
- Responsive design that works on desktop and mobile
- No regression in functionality

**Resources:**
- [FastAPI Templates Documentation](https://fastapi.tiangolo.com/advanced/templates/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

---

### AI-004: Align Testing Framework with Standards

**Priority:** Low  
**Owner:** CTO  
**Due Date:** May 15, 2025  
**Status:** Completed

**Description:**  
The project currently uses `unittest` while our company standards specify Pytest. We need to migrate our tests to align with our standards and improve test coverage.

**Steps:**
1. Convert existing test classes from `unittest` to Pytest style
2. Implement fixtures where appropriate to reduce code duplication
3. Add explicit failure case tests for agent execution
4. Implement parameterized tests for edge cases
5. Add integration tests for the CLI and web interfaces
6. Update CI/CD pipeline to use Pytest
7. Add code coverage reporting

**Success Criteria:**
- All tests passing with Pytest
- Improved test coverage (target: >80%)
- Explicit testing of failure cases
- Comprehensive fixtures for common test scenarios
- CI/CD pipeline updated to use Pytest

**Resources:**
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures Guide](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Parameterization](https://docs.pytest.org/en/stable/parametrize.html)

---

### AI-005: Review Pydantic Usage

**Priority:** Low  
**Owner:** CTO  
**Due Date:** May 15, 2025  
**Status:** Completed

**Description:**  
There is inconsistent use of Pydantic in agent classes. Some configuration parameters are stored as regular instance attributes rather than Pydantic fields, which works but is slightly unconventional.

**Steps:**
1. Review current Pydantic usage across the codebase
2. Decide on a consistent approach (Pydantic fields vs. regular attributes)
3. Update agent classes to follow the chosen approach
4. Add validation for configuration parameters
5. Document the chosen approach for future development
6. Update tests to reflect any changes

**Success Criteria:**
- Consistent Pydantic usage across the codebase
- Proper validation of configuration parameters
- Updated documentation reflecting the chosen approach
- All tests passing with the updated implementation

**Resources:**
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic Best Practices](https://docs.pydantic.dev/latest/usage/best-practices/)

---

### AI-006: Implement Vertex AI Agent Engine Deployment

**Priority:** High  
**Owner:** CTO  
**Due Date:** May 5, 2025  
**Status:** Completed

**Description:**  
Vertex AI Agent Engine is a fully managed service specifically designed for AI agents, offering advantages over traditional Vertex AI endpoints. We need to implement a deployment mechanism for Agent Engine to provide our users with a more robust and scalable deployment option.

**Steps:**
1. Create a new deployment script (`deploy_agent_engine.py`) for Agent Engine deployment
2. Implement environment-specific configuration loading
3. Add support for Google Cloud Storage bucket staging
4. Implement local testing before deployment
5. Add remote testing after deployment
6. Create comprehensive documentation for Agent Engine deployment
7. Update existing documentation to reference the new deployment option

**Success Criteria:**
- Successful deployment of our custom agent to Vertex AI Agent Engine
- Verification that the deployed agent functions correctly
- Comprehensive documentation for Agent Engine deployment
- Updated existing documentation to reference the new deployment option
- End-to-end testing with sample queries

**Resources:**
- [Vertex AI Agent Engine Documentation](https://cloud.google.com/vertex-ai/docs/agent-engine/overview)
- [Google ADK Agent Engine Integration Guide](https://cloud.google.com/vertex-ai/docs/agent-development-kit/agent-engine)

## Next Steps

1. **Team Meeting:** Schedule a team meeting by April 23, 2025, to discuss these action items and assign owners.
2. **Sprint Planning:** Incorporate these items into our next sprint planning session (April 25, 2025).
3. **Documentation Update:** Update our technical documentation to reflect the planned changes by April 26, 2025.
4. **Progress Tracking:** Set up weekly check-ins (every Monday) to track progress on these items.

## Approval

- [ ] CTO
- [ ] Lead Developer
- [ ] Product Manager

## Changelog

| Date | Author | Description |
|------|--------|-------------|
| April 21, 2025 | [Your Name], CTO | Initial creation based on code review report |
| April 21, 2025 | [Your Name], CTO | Implemented AI-001: Fixed Vertex AI Deployment Mechanism |
| April 21, 2025 | [Your Name], CTO | Implemented AI-002: Improved CLI Extensibility |
| April 21, 2025 | [Your Name], CTO | Implemented AI-003: Refactored Local Deployment UI |
| April 21, 2025 | [Your Name], CTO | Started AI-004: Added tests for registry, local deployment UI, and Vertex AI deployment |
| April 21, 2025 | [Your Name], CTO | Continued AI-004: Fixed test failures and improved test coverage |
| April 21, 2025 | [Your Name], CTO | Completed AI-004: Migrated tests from unittest to pytest and added test report |
| April 21, 2025 | [Your Name], CTO | Started AI-005: Reviewed Pydantic usage and created standardization guidelines |
| April 21, 2025 | [Your Name], CTO | Completed AI-005: Implemented hybrid approach for Pydantic usage with validation methods |
| April 21, 2025 | [Your Name], CTO | Implemented AI-006: Added Vertex AI Agent Engine deployment support |
