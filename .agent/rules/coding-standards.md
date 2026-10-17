# Subsystem Rules: Coding Standards

These standards govern code quality across Python, TypeScript, and configuration files.

## 1. Python Guidelines (AI / Model / Backend)
- **Formatting & Style:** Follow PEP 8 conventions.
- **Type Annotations:** Use Python type hints (`typing` / built-in types in 3.13) for all public functions, classes, and API models.
- **Docstrings:** Document all modules, functions, and classes with clear docstrings explaining inputs, outputs, units, and exceptions.
- **Imports:** Group standard library imports, third-party imports, and local imports cleanly. Avoid wildcard imports (`from module import *`).
- **Error Handling:** Catch specific exceptions (`ValueError`, `KeyError`, `FileNotFoundError`) rather than bare `except:`.

## 2. TypeScript / React Guidelines (Frontend)
- **Strict Typing:** Always enable strict mode (`"strict": true` in `tsconfig.json`). Never use `any` unless explicitly justified in comments.
- **Components:** Functional components with typed props interfaces (`interface Props { ... }`).
- **State Management:** Keep state local to components or use lightweight React contexts. Avoid bulky state libraries unless required.
- **Styling:** Use Tailwind CSS utility classes; avoid inline styles. Maintain responsive design principles.

## 3. General Principles
- **DRY (Don't Repeat Yourself):** Extract repeated logic into shared utility modules.
- **Preserve Existing Code:** Preserve existing comments and docstrings unrelated to current edits.
