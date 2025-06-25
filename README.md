# Comic Upload Automation Tool

PyQt desktop application that streamlines the comic publishing workflow for Solar Salvage, automating file management and Git operations.

## What It Does
Transforms comic publishing from a manual multi-step process into a single-click workflow:
1. **Content Input**: UI for selecting comic images and setting metadata (publish date, chapter info, etc.)
2. **File Generation**: Automatically creates properly formatted MDX files with frontmatter
3. **Repository Management**: Copies files to correct locations in Solar Salvage repo structure
4. **Git Automation**: Handles branching, committing, and pushing changes
5. **State Persistence**: Remembers settings (repo paths, last page number, working directories)

## Integration
Purpose-built for the [Solar Salvage](https://github.com/nbamford123/solar-salvage) comic site workflow, generating files that trigger automatic Netlify deployments.
