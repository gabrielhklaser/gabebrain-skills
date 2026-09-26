---
name: arena-ai-controller
description: >-
  Controls the Arena AI platform (https://arena.ai/) in Agent Mode. Use this skill
  whenever the user wants to interact with Arena AI, relay prompts to Arena AI,
  connect GitHub repositories, select branches, or recover lost repository connections
  by opening a new chat and pushing conversation branch changes.
---

# Arena AI Controller Skill

This skill enables Antigravity to automate and control the **Arena AI** platform (`https://arena.ai/`), specializing in **Agent Mode**, GitHub repository integration, and automated failover recovery.

## Capabilities

1. **Persistent Authentication**: Automatically signs in using user credentials and keeps session cookies active.
2. **Prompt Relaying**: Takes user prompts from chat and sends them to Arena AI Agent Mode, streaming and returning the agent's responses.
3. **GitHub Repository & Branch Management**: Automatically enables the GitHub toggle, lists repositories, and selects target repositories and branches.
4. **Automated Failover & Recovery**: If Arena AI loses its connection to the working repository, this skill:
   - Identifies the conversation's active branch.
   - Starts a fresh conversation on Arena AI.
   - Reconnects the GitHub repository and branch.
   - Issues the reload and push instruction so all project changes and history are preserved and pushed to GitHub.

---

## Tooling & Helper Scripts

The automation engine is located at:
`C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py`
and in the workspace scratch at:
`C:\Users\Gabriel\.gemini\antigravity\scratch\arena-controller\arena_agent.py`

### CLI Commands

#### 1. Verify Login & Session Status
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" login
```

#### 2. List Connected GitHub Repositories
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" list-repos
```

#### 3. Send Prompt to Arena AI Agent
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" send --prompt "YOUR PROMPT HERE" --repo "gabrielhklaser/REPO_NAME" --branch "BRANCH_NAME"
```

#### 4. Automatic Reconnection & Push Recovery
When Arena AI drops the repository connection or fails to sync:
```bash
python "C:\Users\Gabriel\.gemini\config\skills\arena-ai-controller\scripts\arena_agent.py" recover-push --repo "gabrielhklaser/REPO_NAME" --branch "BRANCH_NAME"
```

This command will:
1. Open a new chat session at `https://arena.ai/agent`.
2. Connect to the specified GitHub repository and select the branch.
3. Send the command to reload the prior conversation state and push modified files directly to GitHub.
