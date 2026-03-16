# Comprehensive Hooks Reference Guide

**Last Updated:** March 2026
**Source:** Anthropic Agent SDK Documentation
**For:** goodboy behavior-first Claude Code plugin

---

## Table of Contents

1. [Overview](#overview)
2. [Hooks Fundamentals](#hooks-fundamentals)
3. [How Hooks Work](#how-hooks-work)
4. [Available Hooks Reference](#available-hooks-reference)
5. [Configuration Guide](#configuration-guide)
6. [Matchers Deep Dive](#matchers-deep-dive)
7. [Callback Functions](#callback-functions)
8. [Hook Inputs Reference](#hook-inputs-reference)
9. [Hook Outputs Reference](#hook-outputs-reference)
10. [Asynchronous Hooks](#asynchronous-hooks)
11. [Usage Examples](#usage-examples)
12. [Design Patterns](#design-patterns)
13. [Best Practices](#best-practices)
14. [Troubleshooting Guide](#troubleshooting-guide)
15. [Advanced Topics](#advanced-topics)

---

## Overview

Hooks are callback functions that run your code in response to agent events. They provide fine-grained control over agent execution, enabling you to:

- **Block dangerous operations** before they execute (destructive shell commands, unauthorized file access)
- **Log and audit** every tool call for compliance, debugging, or analytics
- **Transform inputs and outputs** to sanitize data, inject credentials, or redirect file paths
- **Require human approval** for sensitive actions (database writes, API calls)
- **Track session lifecycle** to manage state, clean up resources, or send notifications
- **Inject context** into conversations to guide agent behavior
- **Monitor subagent activity** and track parallel task execution
- **Control execution flow** by stopping, pausing, or modifying agent behavior

Hooks are the primary mechanism for implementing **behavior-first** plugin architectures, enforcing organizational policies, and integrating agents with external systems.

---

## Hooks Fundamentals

### Core Concepts

**Hook Event**: A point in agent execution where a callback can be triggered
- Tool use events: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`
- Lifecycle events: `SessionStart`, `SessionEnd`, `Stop`
- User interaction events: `UserPromptSubmit`, `PermissionRequest`, `Notification`
- Subagent events: `SubagentStart`, `SubagentStop`
- System events: `PreCompact`, `Setup`, `ConfigChange`, `TaskCompleted`, `TeammateIdle`, `WorktreeCreate`, `WorktreeRemove`

**Matcher**: A regex pattern that filters when a hook callback fires
- Different hooks match against different fields (tool name, notification type, etc.)
- Optional—omit a matcher to run for every event of that type
- Can combine multiple matchers to create complex filtering logic

**Callback Function**: Your async function that receives event details and returns a decision
- Receives typed input about what's happening
- Can access tool arguments, session ID, working directory, subagent info
- Returns an object controlling whether to allow/deny/modify the operation

**Hook Execution Order**: Hooks execute in the order they appear in the array
- Earlier hooks can block later ones by denying permission
- Later hooks can see the results of earlier hooks' modifications
- Chain multiple hooks for separation of concerns

### When Hooks Don't Work

Hooks don't execute if:
- The agent hits the `max_turns` limit (session ends before hooks can run)
- The event type doesn't exist or the event name is misspelled
- The matcher pattern doesn't match the target field
- The callback times out (exceeds `timeout` value)
- The SDK version doesn't support that hook type

---

## How Hooks Work

Hooks operate in a specific sequence during agent execution:

### Hook Execution Pipeline

```
Agent Event Occurs (e.g., tool call, session start)
    ↓
SDK Checks for Registered Hooks
    ├─ Callback hooks from options.hooks
    └─ Shell command hooks from settings files (if loaded with settingSources)
    ↓
Matchers Filter Applicable Hooks
    ├─ Regex pattern tested against event field (e.g., tool name)
    ├─ Hooks without matchers always match
    └─ Only matching hooks proceed
    ↓
Callback Functions Execute in Order
    ├─ Input data passed to callback
    ├─ Tool use ID provided (correlates PreToolUse/PostToolUse)
    ├─ Context object (signal, agent info) provided
    └─ Callback performs operations (validation, logging, API calls)
    ↓
Callback Returns Decision Object
    ├─ Top-level fields: systemMessage, continue
    └─ hookSpecificOutput: event-specific directives
    ↓
SDK Applies Hook Outputs
    ├─ Block, allow, or modify operation
    ├─ Inject messages into conversation
    ├─ Continue or stop execution
    └─ Append context to results
    ↓
Agent Proceeds with Modified/Approved Operation (or Blocked)
```

### Priority Rules

When multiple hooks apply:
- **Deny takes priority** over ask, which takes priority over allow
- If ANY hook returns `permissionDecision: "deny"`, the operation is blocked
- All hooks execute even if an earlier one denies (the deny is applied at the end)
- For `systemMessage`, all messages are collected and injected
- For `continue: false`, execution stops immediately

---

## Available Hooks Reference

### Hook Event Availability Matrix

| Hook Event | Python SDK | TypeScript SDK | Fires When | Matcher Target | Use Cases |
|-----------|-----------|----------------|-----------|----------------|-----------|
| `PreToolUse` | ✅ Yes | ✅ Yes | Tool call requested (can block/modify) | Tool name | Block dangerous commands, validate input, redirect paths |
| `PostToolUse` | ✅ Yes | ✅ Yes | Tool execution completed successfully | Tool name | Log changes, append context, audit output |
| `PostToolUseFailure` | ✅ Yes | ✅ Yes | Tool execution failed | Tool name | Handle errors, log failures, trigger alerts |
| `UserPromptSubmit` | ✅ Yes | ✅ Yes | User prompt submitted | N/A | Inject context, modify prompts, track input |
| `Stop` | ✅ Yes | ✅ Yes | Agent execution stops | N/A | Save state, cleanup, send notifications |
| `SubagentStart` | ✅ Yes | ✅ Yes | Subagent initializes | N/A | Track parallel tasks, inject context, initialize state |
| `SubagentStop` | ✅ Yes | ✅ Yes | Subagent completes | N/A | Aggregate results, log transcript, cleanup |
| `PreCompact` | ✅ Yes | ✅ Yes | Conversation compaction requested | N/A | Archive transcript, preserve state |
| `PermissionRequest` | ✅ Yes | ✅ Yes | Permission dialog would show | N/A | Custom permission handling, auto-approve |
| `Notification` | ✅ Yes | ✅ Yes | Agent sends status notification | Notification type | Forward to Slack/Discord, integrate webhooks |
| `SessionStart` | ❌ No | ✅ Yes | Session initialization | N/A | Initialize logging, setup telemetry |
| `SessionEnd` | ❌ No | ✅ Yes | Session termination | N/A | Cleanup, finalize reporting, archive logs |
| `Setup` | ❌ No | ✅ Yes | Session setup/maintenance | N/A | Initialize state, load config |
| `TeammateIdle` | ❌ No | ✅ Yes | Teammate becomes idle | N/A | Reassign work, notify inactive agents |
| `TaskCompleted` | ❌ No | ✅ Yes | Background task completes | N/A | Aggregate parallel results |
| `ConfigChange` | ❌ No | ✅ Yes | Configuration file changes | N/A | Reload settings dynamically |
| `WorktreeCreate` | ❌ No | ✅ Yes | Git worktree created | N/A | Track isolated workspaces |
| `WorktreeRemove` | ❌ No | ✅ Yes | Git worktree removed | N/A | Cleanup workspace resources |

### Tool Hooks Deep Dive

#### PreToolUse Hook

**Fires**: Before a tool executes (can block or modify)
**Priority**: Highest—use to validate and control tool execution
**Can**: Block operation, modify input, auto-approve, inject context
**Cannot**: Access tool output (it hasn't executed yet)

```typescript
// TypeScript signature
PreToolUse: [
  {
    matcher: "Bash|Read|Write",  // Optional regex on tool name
    timeout: 60,                  // Seconds
    hooks: [myCallback]           // Callback function
  }
]
```

**Common Use Cases**:
- Block dangerous commands (e.g., `rm -rf /`, destructive operations)
- Validate file paths (prevent writing to system directories)
- Redirect file operations to sandboxed directories
- Auto-approve read-only tools (Read, Glob, Grep)
- Inject credentials or environment variables
- Rate limit tool usage
- Require approval workflows for sensitive operations

**Input Example**:
```json
{
  "hook_event_name": "PreToolUse",
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/etc/passwd",
    "content": "..."
  },
  "session_id": "sess_123",
  "cwd": "/home/user",
  "agent_id": "agent_456",          // If in subagent
  "agent_type": "research"           // If in subagent
}
```

**Output Decision**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny|allow|ask",
    "permissionDecisionReason": "Writing to /etc is protected",
    "updatedInput": {
      "file_path": "/sandbox/passwd",
      "content": "..."
    }
  }
}
```

---

#### PostToolUse Hook

**Fires**: After a tool executes successfully
**Priority**: Lower than PreToolUse—used for auditing and context injection
**Can**: Log results, append context to output, stop execution
**Cannot**: Block the operation (already executed), modify inputs

```typescript
PostToolUse: [
  {
    matcher: "Write|Edit|Delete",  // Optional
    hooks: [auditLogger, contextInjector]
  }
]
```

**Common Use Cases**:
- Audit logging (record all file changes, API calls)
- Integration webhooks (notify external systems)
- Context injection (append related information)
- Analytics and metrics collection
- State tracking and history recording
- Compliance reporting

**Input Example**:
```json
{
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "git log --oneline" },
  "tool_output": "abc123 Fix bug\ndef456 Add feature",
  "session_id": "sess_123",
  "cwd": "/repo"
}
```

**Output Options**:
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Executed by approved service account"
  },
  "systemMessage": "Logged operation to audit trail"
}
```

---

#### PostToolUseFailure Hook

**Fires**: When a tool execution fails (errors, exceptions)
**Priority**: For error handling and recovery
**Can**: Log failures, inject error context, stop execution
**Cannot**: Retry the tool or modify the error

```typescript
PostToolUseFailure: [
  {
    matcher: "Bash",
    hooks: [errorHandler, alertSystem]
  }
]
```

**Common Use Cases**:
- Error logging and diagnostics
- Alerting systems on critical failures
- Graceful degradation handling
- User-friendly error messages
- Failure analytics and trending

**Input Example**:
```json
{
  "hook_event_name": "PostToolUseFailure",
  "tool_name": "Bash",
  "tool_input": { "command": "rm important_file.txt" },
  "error": "Permission denied",
  "error_code": 1,
  "session_id": "sess_123"
}
```

---

### User Interaction Hooks

#### UserPromptSubmit Hook

**Fires**: When user submits a prompt
**Matcher**: N/A (matches all user prompts)
**Can**: Inject context, modify prompt, inject system message
**Cannot**: Block the prompt entirely

```typescript
UserPromptSubmit: [
  {
    hooks: [contextInjector, promptModifier]
  }
]
```

**Common Use Cases**:
- Inject system context about user/organization
- Add relevant background information
- Track user prompts for analytics
- Apply content filters or policies
- Augment prompts with retrieved documents

**Input Example**:
```json
{
  "hook_event_name": "UserPromptSubmit",
  "user_prompt": "How do I deploy to production?",
  "session_id": "sess_123",
  "cwd": "/repo"
}
```

**Output Example**:
```json
{
  "systemMessage": "This is a deployment question. Consider checking the deployment guide at docs/deployment.md",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit"
  }
}
```

---

#### PermissionRequest Hook

**Fires**: When a permission dialog would be displayed
**Use**: Custom permission handling, auto-approval workflows
**Can**: Custom permission logic, auto-approve, inject guidance

```typescript
PermissionRequest: [
  {
    hooks: [customPermissionHandler]
  }
]
```

**Common Use Cases**:
- Custom permission policies
- Auto-approval for trusted operations
- Integration with external authorization systems
- Custom permission UI

---

#### Notification Hook

**Fires**: When agent sends status notifications
**Matcher**: Notification type (`permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`)
**Notification Types**:
- `permission_prompt`: Claude needs permission for an operation
- `idle_prompt`: Claude is waiting for input
- `auth_success`: Authentication completed
- `elicitation_dialog`: Claude is prompting user for information

```typescript
Notification: [
  {
    matcher: "permission_prompt|auth_success",  // Optional
    hooks: [slackNotifier, emailNotifier]
  }
]
```

**Common Use Cases**:
- Forward to Slack/Discord/Teams
- Email notifications for important events
- Integration with incident management systems
- Custom notification formatting
- Audit logging of all permission requests

**Input Example**:
```json
{
  "hook_event_name": "Notification",
  "notification_type": "permission_prompt",
  "message": "Permission needed to execute bash command",
  "title": "Bash Permission Required",
  "session_id": "sess_123"
}
```

---

### Lifecycle Hooks

#### Stop Hook

**Fires**: When agent execution stops (normally or early termination)
**Use**: Cleanup, state saving, final reporting
**Can**: Save state, send notifications, cleanup resources

```typescript
Stop: [
  {
    hooks: [saveState, sendReport, cleanup]
  }
]
```

**Common Use Cases**:
- Save session state
- Generate final reports
- Cleanup temporary resources
- Send completion notifications
- Archive logs
- Close database connections

**Input Example**:
```json
{
  "hook_event_name": "Stop",
  "stop_reason": "user_requested|max_turns|error|completed",
  "session_id": "sess_123",
  "cwd": "/repo"
}
```

---

#### SessionStart Hook (TypeScript Only)

**Fires**: When session initializes
**Use**: Setup, initialization, telemetry
**Available**: TypeScript SDK only
**Python Alternative**: Use first message from `client.receive_response()`

```typescript
SessionStart: [
  {
    hooks: [initializeLogging, setupTelemetry]
  }
]
```

**Common Use Cases**:
- Initialize logging infrastructure
- Setup performance monitoring
- Load configuration
- Authenticate with external services
- Initialize session state

---

#### SessionEnd Hook (TypeScript Only)

**Fires**: When session terminates
**Use**: Cleanup, finalization
**Available**: TypeScript SDK only

```typescript
SessionEnd: [
  {
    hooks: [finalizeMetrics, closeConnections]
  }
]
```

---

### Subagent Hooks

#### SubagentStart Hook

**Fires**: When a subagent initializes
**Use**: Track parallel execution, initialize subagent state
**Can**: Log startup, inject context, track spawning

```typescript
SubagentStart: [
  {
    hooks: [trackSubagent, initializeSubagentLogging]
  }
]
```

**Input Example**:
```json
{
  "hook_event_name": "SubagentStart",
  "agent_id": "subagent_789",
  "agent_type": "research",
  "session_id": "sess_123"
}
```

---

#### SubagentStop Hook

**Fires**: When a subagent completes
**Use**: Aggregate results, track completion
**Can**: Log results, aggregate outputs, cleanup resources

```typescript
SubagentStop: [
  {
    hooks: [aggregateResults, archiveTranscript]
  }
]
```

**Input Example**:
```json
{
  "hook_event_name": "SubagentStop",
  "agent_id": "subagent_789",
  "agent_type": "research",
  "agent_transcript_path": "/tmp/subagent_transcript.txt",
  "stop_hook_active": true,
  "session_id": "sess_123"
}
```

**Common Use Cases**:
- Aggregate results from parallel tasks
- Merge outputs from multiple subagents
- Track completion status
- Cleanup subagent resources
- Archive transcripts for audit

---

### System Hooks (Advanced)

#### PreCompact Hook

**Fires**: Before conversation compaction (summarization)
**Use**: Archive transcript, preserve state

```typescript
PreCompact: [
  {
    hooks: [archiveTranscript]
  }
]
```

---

#### Setup Hook (TypeScript Only)

**Fires**: During session setup/maintenance
**Use**: Initialize state, load config

```typescript
Setup: [
  {
    hooks: [loadConfiguration]
  }
]
```

---

#### ConfigChange Hook (TypeScript Only)

**Fires**: When configuration file changes
**Use**: Reload settings dynamically

```typescript
ConfigChange: [
  {
    hooks: [reloadSettings]
  }
]
```

---

#### WorktreeCreate/WorktreeRemove Hooks (TypeScript Only)

**Fires**: When git worktrees are created/removed
**Use**: Track isolated workspaces, cleanup

```typescript
WorktreeCreate: [
  {
    hooks: [trackWorktree]
  }
],
WorktreeRemove: [
  {
    hooks: [cleanupWorktree]
  }
]
```

---

## Configuration Guide

### Basic Configuration

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher

# Define your hooks
async def validate_command(input_data, tool_use_id, context):
    # Your hook logic
    return {}

# Configure options with hooks
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(
                matcher="Bash",
                hooks=[validate_command],
                timeout=30
            )
        ]
    }
)

# Use with SDK
async with ClaudeSDKClient(options=options) as client:
    await client.query("Run some command")
```

```typescript
import { query, HookCallback } from "@anthropic-ai/claude-agent-sdk";

const validateCommand: HookCallback = async (input, toolUseID, { signal }) => {
  // Your hook logic
  return {};
};

for await (const message of query({
  prompt: "Run some command",
  options: {
    hooks: {
      PreToolUse: [
        {
          matcher: "Bash",
          hooks: [validateCommand],
          timeout: 30
        }
      ]
    }
  }
})) {
  console.log(message);
}
```

### Hook Configuration Object

```typescript
interface HookConfiguration {
  // Key: hook event name (PreToolUse, PostToolUse, etc)
  // Value: array of matchers
  [hookEventName: string]: HookMatcher[];
}

interface HookMatcher {
  matcher?: string;              // Regex pattern (optional)
  hooks: HookCallback[];         // Array of callbacks
  timeout?: number;              // Timeout in seconds (default: 60)
}

interface HookCallback {
  (input: HookInput, toolUseID: string | undefined, context: HookContext): Promise<HookOutput>;
}
```

### Loading Shell Command Hooks from Settings

```python
# Load hooks defined in .claude/settings.json
options = ClaudeAgentOptions(
    setting_sources=["project"]  # Loads .claude/settings.json
)
```

```typescript
const options = {
  settingSources: ["project"]  // Loads .claude/settings.json
};
```

---

## Matchers Deep Dive

### Matcher Fundamentals

Matchers are regex patterns that filter when callbacks execute. Different hook types match against different fields:

| Hook Type | Matches Against | Examples |
|-----------|-----------------|----------|
| Tool hooks (PreToolUse, PostToolUse, PostToolUseFailure) | Tool name | `Bash`, `Write`, `Edit`, `Read`, `Glob`, `Grep` |
| Notification hook | Notification type | `permission_prompt`, `idle_prompt`, `auth_success` |
| Subagent hooks | N/A (no matching) | Use without matcher |
| Lifecycle hooks | N/A (no matching) | Use without matcher |

### Built-in Tool Names

```
Bash              # Execute shell commands
Read              # Read file contents
Write             # Create/overwrite files
Edit              # Modify files
Glob              # Find files by pattern
Grep              # Search file contents
WebFetch          # Fetch web content
WebSearch         # Search the web
Agent             # Create subagents
```

### MCP Tool Naming

MCP tools use format: `mcp__<server>__<action>`

Examples:
- `mcp__playwright__browser_screenshot`
- `mcp__slack__post_message`
- `mcp__github__create_issue`
- `mcp__postgresql__execute_query`

### Regex Matcher Patterns

```python
# Match single tool
matcher="Bash"                     # Only Bash tool

# Match multiple tools (OR pattern)
matcher="Write|Edit|Delete"        # Write, Edit, or Delete

# Match all MCP tools
matcher="^mcp__"                   # Any tool starting with mcp__

# Match specific MCP server
matcher="^mcp__slack__"            # All Slack MCP tools

# Match read-only tools
matcher="Read|Glob|Grep"           # File read operations

# Complex patterns
matcher="(Bash|Bash.*)|^mcp__ssh__"  # Bash tools or SSH MCP tools

# No matcher (matches everything)
matcher=None/undefined             # All tools of that hook type
```

### Matcher Execution Order

Hooks execute in order they appear:

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[check_rate_limit]),      # First
            HookMatcher(matcher="Bash", hooks=[validate_command]),      # Second
            HookMatcher(matcher="Write|Edit", hooks=[file_audit]),      # Third
            HookMatcher(hooks=[global_logger]),                          # Last (no matcher)
        ]
    }
)
```

Execution order:
1. First `Bash` hook runs
2. If allowed, second `Bash` hook runs
3. If both allow and it's a write tool, file audit runs
4. Global logger runs for everything

### Important: Matchers Don't Filter Arguments

Matchers filter by **tool name only**. To filter by file path or arguments, check inside your callback:

```python
async def protect_env_files(input_data, tool_use_id, context):
    file_path = input_data["tool_input"].get("file_path", "")

    # Check file path inside callback, not in matcher
    if file_path.endswith(".env"):
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "Cannot modify .env files"
            }
        }

    return {}
```

---

## Callback Functions

### Callback Signature

```python
# Python
async def my_hook(
    input_data: dict,           # Hook-specific input data
    tool_use_id: str | None,    # Correlates PreToolUse/PostToolUse
    context: Any                # Reserved for future use
) -> dict:
    # Return hook output
    return {}
```

```typescript
// TypeScript
const myHook: HookCallback = async (
  input: HookInput,             // Hook-specific input data
  toolUseID: string | undefined, // Correlates PreToolUse/PostToolUse
  context: { signal: AbortSignal } // For cancellation
): Promise<HookOutput> => {
  // Return hook output
  return {};
};
```

### Input Data Structure

All hook inputs contain common fields:

```python
{
    "hook_event_name": "PreToolUse",  # The hook type
    "session_id": "sess_123",         # Unique session ID
    "cwd": "/home/user/project",      # Current working directory

    # Subagent context (PreToolUse, PostToolUse, PostToolUseFailure only)
    "agent_id": "subagent_456",       # Subagent ID if running in subagent
    "agent_type": "research",         # Subagent type if running in subagent

    # Tool-specific fields (depend on hook type)
    "tool_name": "Bash",              # For PreToolUse, PostToolUse
    "tool_input": {...},              # Tool arguments
    "tool_output": "...",             # Result (PostToolUse only)
    "error": "...",                   # Error message (PostToolUseFailure only)
}
```

### Tool Use ID Correlation

The `tool_use_id` parameter links `PreToolUse` and `PostToolUse` events:

```python
tool_use_ids = {}

async def pre_hook(input_data, tool_use_id, context):
    # Store tool use ID on PreToolUse
    tool_use_ids[tool_use_id] = {
        "tool": input_data["tool_name"],
        "started": datetime.now()
    }
    return {}

async def post_hook(input_data, tool_use_id, context):
    # Look up using same tool_use_id on PostToolUse
    if tool_use_id in tool_use_ids:
        start = tool_use_ids[tool_use_id]["started"]
        duration = datetime.now() - start
        print(f"Tool {input_data['tool_name']} took {duration}")
    return {}
```

### Context Object (TypeScript)

TypeScript callbacks receive a context object with cancellation support:

```typescript
const myHook: HookCallback = async (input, toolUseID, { signal }) => {
  try {
    // Use signal for HTTP requests
    const response = await fetch("https://api.example.com/check", {
      signal  // Cancellation support
    });
    return {};
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      console.log("Hook cancelled");
    } else {
      console.error("Hook error:", error);
    }
    throw error;  // Or handle gracefully
  }
};
```

---

## Hook Inputs Reference

### PreToolUse Hook Input

```python
{
    "hook_event_name": "PreToolUse",
    "tool_name": "Bash",                      # Which tool is being called
    "tool_input": {
        "command": "git push origin main"     # Tool arguments
    },
    "session_id": "sess_abc123",
    "cwd": "/home/user/repo",

    # Subagent context (if applicable)
    "agent_id": "agent_xyz789",
    "agent_type": "research"
}
```

### PostToolUse Hook Input

```python
{
    "hook_event_name": "PostToolUse",
    "tool_name": "Bash",
    "tool_input": {
        "command": "git log --oneline"
    },
    "tool_output": "abc123 Fix bug\ndef456 Add feature",
    "session_id": "sess_abc123",
    "cwd": "/home/user/repo",

    # Subagent context (if applicable)
    "agent_id": "agent_xyz789",
    "agent_type": "research"
}
```

### PostToolUseFailure Hook Input

```python
{
    "hook_event_name": "PostToolUseFailure",
    "tool_name": "Bash",
    "tool_input": {
        "command": "invalid command"
    },
    "error": "Command not found",             # Error message
    "error_code": 127,                        # Exit code (if applicable)
    "session_id": "sess_abc123",
    "cwd": "/home/user/repo",

    # Subagent context (if applicable)
    "agent_id": "agent_xyz789",
    "agent_type": "research"
}
```

### UserPromptSubmit Hook Input

```python
{
    "hook_event_name": "UserPromptSubmit",
    "user_prompt": "How do I deploy this to production?",
    "session_id": "sess_abc123",
    "cwd": "/home/user/repo"
}
```

### Notification Hook Input

```python
{
    "hook_event_name": "Notification",
    "notification_type": "permission_prompt",  # or auth_success, idle_prompt, etc
    "message": "Permission needed to execute: bash",
    "title": "Bash Permission Required",      # Optional
    "session_id": "sess_abc123"
}
```

### SubagentStart Hook Input

```python
{
    "hook_event_name": "SubagentStart",
    "agent_id": "subagent_xyz789",
    "agent_type": "research",
    "session_id": "sess_abc123"
}
```

### SubagentStop Hook Input

```python
{
    "hook_event_name": "SubagentStop",
    "agent_id": "subagent_xyz789",
    "agent_type": "research",
    "agent_transcript_path": "/tmp/subagent_transcript_xyz789.txt",
    "stop_hook_active": True,                 # Is Stop hook registered?
    "session_id": "sess_abc123"
}
```

### Stop Hook Input

```python
{
    "hook_event_name": "Stop",
    "stop_reason": "user_requested",          # user_requested, max_turns, error, completed
    "session_id": "sess_abc123",
    "cwd": "/home/user/repo"
}
```

---

## Hook Outputs Reference

### Output Structure

Every hook returns an object with this structure:

```python
{
    # Top-level fields (optional)
    "systemMessage": "Optional message to inject into conversation",
    "continue_": False,                        # Stop execution (Python: continue_)

    # Hook-specific output (optional)
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",         # Which hook type

        # For permission hooks (PreToolUse, PermissionRequest)
        "permissionDecision": "allow|deny|ask",
        "permissionDecisionReason": "Optional explanation",

        # For input modification (PreToolUse)
        "updatedInput": {
            "file_path": "/new/path",          # Modified arguments
            # ... other modified tool input fields
        },

        # For context injection (PostToolUse)
        "additionalContext": "Optional context to append to result",

        # Async operations
        "async_": True,                        # Python: async_ (avoid keyword)
        "asyncTimeout": 30000,                 # Milliseconds
    }
}
```

### Return Values by Hook Type

#### PreToolUse Outputs

```python
# Block operation
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Protected directory"
    }
}

# Allow with modifications
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "updatedInput": {
            "file_path": "/sandbox/file.txt",
            "content": input_data["tool_input"]["content"]
        }
    }
}

# Auto-approve
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Read-only operation"
    }
}

# Ask user for permission
return {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Sensitive operation"
    }
}

# Allow and inject context
return {
    "systemMessage": "This is a sensitive operation",
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow"
    }
}
```

#### PostToolUse Outputs

```python
# Append additional context
return {
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "Logged to audit trail"
    }
}

# Inject message into conversation
return {
    "systemMessage": "File operation completed and verified"
}

# Empty output (just log the event)
return {}
```

#### UserPromptSubmit Outputs

```python
# Inject context
return {
    "systemMessage": "Here's relevant context about the deployment process..."
}

# Stop execution
return {
    "continue_": False,  # Python, use continue_
    "systemMessage": "User prompt violates policy"
}
```

#### Notification Hook Outputs

```python
# Notification hooks typically return empty (they're side effects)
return {}
```

#### Stop Hook Outputs

```python
# Can save state, send notifications
return {
    "systemMessage": "Session archived for audit"
}
```

---

## Asynchronous Hooks

### When to Use Async Output

Use async output when your hook performs side effects (logging, webhooks, API calls) that don't need to influence the agent's behavior. This tells the agent to continue immediately without waiting.

### Async Configuration

```python
async def async_logger(input_data, tool_use_id, context):
    # Start background task
    asyncio.create_task(send_to_logging_service(input_data))

    # Return immediately (don't wait for send_to_logging_service)
    return {
        "async_": True,              # Python: async_ (reserved keyword)
        "asyncTimeout": 30000        # 30 seconds for background task
    }
```

```typescript
const asyncLogger: HookCallback = async (input, toolUseID, { signal }) => {
  // Start background task
  sendToLoggingService(input).catch(console.error);

  // Return immediately (don't wait for sendToLoggingService)
  return {
    async: true,                    // TypeScript: async
    asyncTimeout: 30000             // 30 seconds
  };
};
```

### Important Async Limitations

⚠️ **Async outputs cannot:**
- Block or modify the operation
- Inject context or system messages
- Stop execution

✅ **Use async outputs for:**
- Logging
- Metrics collection
- Webhook notifications
- External system integration
- Audit trails

### Async Timeout

The `asyncTimeout` field specifies how long (in milliseconds) the SDK waits for your background task to complete before considering it finished. Set based on your operation duration:

```python
{
    "async_": True,
    "asyncTimeout": 5000        # 5 seconds for quick webhooks
}

{
    "async_": True,
    "asyncTimeout": 60000       # 60 seconds for API calls with retry
}
```

---

## Usage Examples

### Example 1: Block Dangerous Shell Commands

```python
import re
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, HookMatcher

async def protect_destructive_commands(input_data, tool_use_id, context):
    """Block dangerous shell commands before execution."""

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    if input_data["tool_name"] != "Bash":
        return {}

    command = input_data["tool_input"].get("command", "")

    # Dangerous patterns to block
    dangerous_patterns = [
        r"rm\s+-rf\s+/",           # rm -rf /
        r"dd\s+if=/dev/zero",      # Overwrite disk
        r":(){ :|:& };:",           # Fork bomb
        r"wget.*-O.*\|.*bash",      # Remote code execution
        r"curl.*\|.*bash",          # Remote code execution
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command):
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Dangerous command blocked: {pattern}"
                }
            }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[protect_destructive_commands])
        ]
    }
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Clean up old logs and temp files")
```

### Example 2: Redirect File Operations to Sandbox

```python
async def redirect_to_sandbox(input_data, tool_use_id, context):
    """Redirect all file writes to a sandboxed directory."""

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    tool_name = input_data["tool_name"]
    tool_input = input_data["tool_input"]

    # Apply to file-writing tools
    if tool_name in ["Write", "Edit", "Delete"]:
        original_path = tool_input.get("file_path", "")

        # Redirect to sandbox
        sandboxed_path = f"/sandbox{original_path}"

        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": f"Redirected to sandbox",
                "updatedInput": {
                    **tool_input,
                    "file_path": sandboxed_path
                }
            }
        }

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit|Delete", hooks=[redirect_to_sandbox])
        ]
    }
)
```

### Example 3: Audit Logging with Timestamps

```python
import json
from datetime import datetime
from claude_agent_sdk import HookMatcher, ClaudeAgentOptions

async def audit_logger(input_data, tool_use_id, context):
    """Log all tool usage to an audit trail."""

    if input_data["hook_event_name"] not in ["PostToolUse", "PostToolUseFailure"]:
        return {}

    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": input_data["session_id"],
        "tool": input_data["tool_name"],
        "input": input_data.get("tool_input"),
        "cwd": input_data.get("cwd"),
        "event": input_data["hook_event_name"]
    }

    if "tool_output" in input_data:
        audit_entry["output"] = input_data["tool_output"]

    if "error" in input_data:
        audit_entry["error"] = input_data["error"]

    # Write to audit log (blocking operation)
    with open("/var/log/audit_trail.jsonl", "a") as f:
        f.write(json.dumps(audit_entry) + "\n")

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [HookMatcher(hooks=[audit_logger])],
        "PostToolUseFailure": [HookMatcher(hooks=[audit_logger])]
    }
)
```

### Example 4: Rate Limiting Tool Usage

```python
from collections import defaultdict
from datetime import datetime, timedelta

tool_usage = defaultdict(list)
MAX_CALLS_PER_MINUTE = 10

async def rate_limiter(input_data, tool_use_id, context):
    """Rate limit tool usage to prevent abuse."""

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    tool_name = input_data["tool_name"]
    session_id = input_data["session_id"]

    # Track usage by tool and session
    key = f"{session_id}:{tool_name}"
    now = datetime.utcnow()

    # Remove old entries (older than 1 minute)
    tool_usage[key] = [
        timestamp for timestamp in tool_usage[key]
        if now - timestamp < timedelta(minutes=1)
    ]

    # Check if limit exceeded
    if len(tool_usage[key]) >= MAX_CALLS_PER_MINUTE:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Rate limit exceeded: {MAX_CALLS_PER_MINUTE} calls per minute"
            }
        }

    # Record this call
    tool_usage[key].append(now)

    return {}
```

### Example 5: Auto-approve Read-only Tools

```python
async def auto_approve_reads(input_data, tool_use_id, context):
    """Auto-approve read-only filesystem operations."""

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    read_only_tools = ["Read", "Glob", "Grep", "WebFetch", "WebSearch"]

    if input_data["tool_name"] in read_only_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "permissionDecisionReason": "Read-only operation auto-approved"
            }
        }

    return {}
```

### Example 6: Forward Notifications to Slack

```python
import asyncio
import json
from aiohttp import ClientSession

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

async def slack_notifier(input_data, tool_use_id, context):
    """Forward agent notifications to Slack."""

    if input_data["hook_event_name"] != "Notification":
        return {}

    notification_type = input_data.get("notification_type", "")
    message = input_data.get("message", "")
    title = input_data.get("title", "")

    # Format for Slack
    slack_message = {
        "text": f"{title}: {message}" if title else message,
        "attachments": [
            {
                "color": "warning" if "permission" in notification_type else "good",
                "fields": [
                    {
                        "title": "Type",
                        "value": notification_type,
                        "short": True
                    },
                    {
                        "title": "Session",
                        "value": input_data.get("session_id", "unknown"),
                        "short": True
                    }
                ]
            }
        ]
    }

    # Send to Slack (async)
    try:
        async with ClientSession() as session:
            await session.post(
                SLACK_WEBHOOK_URL,
                json=slack_message,
                timeout=5
            )
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")

    return {}
```

### Example 7: Inject Context from Documentation

```python
async def inject_deployment_context(input_data, tool_use_id, context):
    """Inject deployment documentation when user asks about it."""

    if input_data["hook_event_name"] != "UserPromptSubmit":
        return {}

    prompt = input_data.get("user_prompt", "").lower()

    # Check if user is asking about deployment
    deployment_keywords = ["deploy", "production", "release", "ship", "launch"]

    if any(keyword in prompt for keyword in deployment_keywords):
        # Read deployment guide
        try:
            with open("docs/DEPLOYMENT.md", "r") as f:
                deployment_guide = f.read()

            return {
                "systemMessage": f"Here's our deployment guide:\n\n{deployment_guide}"
            }
        except FileNotFoundError:
            pass

    return {}
```

### Example 8: Track Subagent Execution

```python
subagent_results = {}

async def track_subagent_start(input_data, tool_use_id, context):
    """Track when subagent starts."""

    if input_data["hook_event_name"] != "SubagentStart":
        return {}

    agent_id = input_data["agent_id"]
    agent_type = input_data["agent_type"]

    subagent_results[agent_id] = {
        "type": agent_type,
        "session_id": input_data["session_id"],
        "started_at": datetime.utcnow().isoformat()
    }

    print(f"[SUBAGENT START] {agent_id} ({agent_type})")

    return {}

async def track_subagent_stop(input_data, tool_use_id, context):
    """Track when subagent completes."""

    if input_data["hook_event_name"] != "SubagentStop":
        return {}

    agent_id = input_data["agent_id"]
    transcript_path = input_data.get("agent_transcript_path")

    if agent_id in subagent_results:
        subagent_results[agent_id]["completed_at"] = datetime.utcnow().isoformat()
        subagent_results[agent_id]["transcript"] = transcript_path

    print(f"[SUBAGENT STOP] {agent_id}")
    print(f"  Transcript: {transcript_path}")

    return {}
```

### Example 9: Chain Multiple Hooks with Different Concerns

```python
# Separate concerns: validation, transformation, logging

async def validate_permissions(input_data, tool_use_id, context):
    """First: Check if operation is allowed."""
    protected_paths = ["/etc", "/root", "/sys", "/proc"]

    if input_data["tool_name"] in ["Write", "Edit", "Delete"]:
        file_path = input_data["tool_input"].get("file_path", "")

        if any(file_path.startswith(p) for p in protected_paths):
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Protected system directory"
                }
            }

    return {}

async def transform_paths(input_data, tool_use_id, context):
    """Second: Transform paths to sandbox."""
    if input_data["tool_name"] in ["Write", "Edit", "Delete"]:
        file_path = input_data["tool_input"].get("file_path", "")

        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "allow",
                "updatedInput": {
                    **input_data["tool_input"],
                    "file_path": f"/sandbox{file_path}"
                }
            }
        }

    return {}

async def log_all_operations(input_data, tool_use_id, context):
    """Third: Log after validation and transformation."""
    print(f"[{input_data['hook_event_name']}] {input_data['tool_name']}")
    print(f"  Input: {input_data.get('tool_input')}")

    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(hooks=[validate_permissions]),      # First
            HookMatcher(hooks=[transform_paths]),           # Second
            HookMatcher(hooks=[log_all_operations])         # Third
        ]
    }
)
```

### Example 10: Require Approval for Sensitive Operations

```python
SENSITIVE_COMMANDS = [
    "delete",
    "drop",
    "truncate",
    "rm -f",
    "git push --force"
]

async def require_approval_for_sensitive(input_data, tool_use_id, context):
    """Require user approval for sensitive operations."""

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    if input_data["tool_name"] != "Bash":
        return {}

    command = input_data["tool_input"].get("command", "").lower()

    for sensitive_cmd in SENSITIVE_COMMANDS:
        if sensitive_cmd in command:
            return {
                "systemMessage": f"⚠️ This command is sensitive and requires review: {sensitive_cmd}",
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"Sensitive operation: {sensitive_cmd}"
                }
            }

    return {}
```

---

## Design Patterns

### Pattern 1: Permission Tiers

Implement different permission levels for different operations:

```python
PERMISSION_LEVELS = {
    "admin": ["Bash", "Write", "Edit", "Delete", "Agent"],
    "user": ["Read", "Glob", "Grep", "WebFetch"],
    "viewer": ["Read", "Glob", "Grep"]
}

current_user_level = "user"  # Set based on actual user

async def permission_tier_check(input_data, tool_use_id, context):
    tool_name = input_data["tool_name"]

    allowed_tools = PERMISSION_LEVELS.get(current_user_level, [])

    if tool_name not in allowed_tools:
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Permission denied: {current_user_level} cannot use {tool_name}"
            }
        }

    return {}
```

### Pattern 2: Progressive Disclosure

Start permissive, then become restrictive based on action:

```python
risky_commands_executed = 0

async def progressive_restriction(input_data, tool_use_id, context):
    global risky_commands_executed

    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    risky_keywords = ["delete", "drop", "truncate"]
    command = input_data.get("tool_input", {}).get("command", "").lower()

    is_risky = any(kw in command for kw in risky_keywords)

    if is_risky:
        # First risky: allow but warn
        if risky_commands_executed == 0:
            return {
                "systemMessage": "⚠️ Risky operation detected"
            }

        # Second risky: ask
        elif risky_commands_executed == 1:
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "ask"
                }
            }

        # Third and beyond: deny
        else:
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Too many risky operations"
                }
            }

        risky_commands_executed += 1

    return {}
```

### Pattern 3: Context Injection Pipeline

Build context from multiple sources:

```python
async def load_project_context(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "UserPromptSubmit":
        return {}

    contexts = []

    # Load README
    try:
        with open("README.md") as f:
            contexts.append(f"PROJECT:\n{f.read()}")
    except FileNotFoundError:
        pass

    # Load standards
    try:
        with open("STANDARDS.md") as f:
            contexts.append(f"STANDARDS:\n{f.read()}")
    except FileNotFoundError:
        pass

    # Load recent changes
    try:
        with open("CHANGELOG.md") as f:
            contexts.append(f"RECENT:\n{f.read()}")
    except FileNotFoundError:
        pass

    if contexts:
        return {
            "systemMessage": "\n\n".join(contexts)
        }

    return {}
```

### Pattern 4: Audit Trail with Correlation

Track related operations across tool calls:

```python
import uuid
from collections import defaultdict

correlation_groups = defaultdict(list)
current_correlation_id = None

async def start_correlation_on_user_input(input_data, tool_use_id, context):
    global current_correlation_id

    if input_data["hook_event_name"] == "UserPromptSubmit":
        current_correlation_id = str(uuid.uuid4())
        print(f"[CORRELATION] New group: {current_correlation_id}")

    return {}

async def log_with_correlation(input_data, tool_use_id, context):
    if input_data["hook_event_name"] in ["PostToolUse", "PostToolUseFailure"]:
        event = {
            "correlation_id": current_correlation_id,
            "tool": input_data["tool_name"],
            "session": input_data["session_id"],
            "timestamp": datetime.utcnow().isoformat()
        }

        correlation_groups[current_correlation_id].append(event)
        print(f"[AUDIT] {event}")

    return {}
```

### Pattern 5: Graceful Degradation

Fall back to safer alternatives when risky operations are blocked:

```python
async def suggest_alternatives(input_data, tool_use_id, context):
    if input_data["hook_event_name"] != "PreToolUse":
        return {}

    blocked_commands = {
        "rm -rf": "Use git to track files, or mark as archived instead",
        "DROP TABLE": "Archive data first, then delete after review",
        "git push --force": "Use git rebase -i to clean history safely"
    }

    command = input_data.get("tool_input", {}).get("command", "")

    for risky_cmd, alternative in blocked_commands.items():
        if risky_cmd in command:
            return {
                "systemMessage": f"⚠️ Blocked: {risky_cmd}\n\nAlternative: {alternative}",
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Use safer alternative instead"
                }
            }

    return {}
```

---

## Best Practices

### 1. Keep Hooks Focused

Each hook should have a single responsibility:

```python
# ❌ Bad: Too many concerns in one hook
async def kitchen_sink(input_data, tool_use_id, context):
    # Validate
    # Transform
    # Log
    # Send webhook
    # Update database
    # ...
    return {}

# ✅ Good: Separate hooks
async def validate(input_data, tool_use_id, context):
    # Just validate
    return {}

async def transform(input_data, tool_use_id, context):
    # Just transform
    return {}

async def audit_log(input_data, tool_use_id, context):
    # Just log
    return {}
```

### 2. Use Matchers to Filter

Don't process irrelevant events:

```python
# ❌ Bad: Check inside callback
async def file_protector(input_data, tool_use_id, context):
    if input_data["tool_name"] not in ["Write", "Edit"]:
        return {}
    # ...

# ✅ Good: Use matcher
HookMatcher(
    matcher="Write|Edit",
    hooks=[file_protector]
)
```

### 3. Handle Errors Gracefully

Don't let hook errors break agent execution:

```python
# ❌ Bad: Can crash if API is down
async def send_webhook(input_data, tool_use_id, context):
    response = await fetch("https://api.example.com/webhook")
    return {}

# ✅ Good: Catch and handle errors
async def send_webhook(input_data, tool_use_id, context):
    try:
        response = await fetch("https://api.example.com/webhook")
    except Exception as e:
        print(f"Webhook failed: {e}")  # Log but don't crash

    return {}  # Still return success
```

### 4. Use Async Output for Side Effects

Don't block agent for slow operations:

```python
# ❌ Bad: Blocks agent for 5 seconds
async def slow_logging(input_data, tool_use_id, context):
    await send_to_remote_logging_service(input_data)  # 5 seconds
    return {}

# ✅ Good: Fire and forget
async def slow_logging(input_data, tool_use_id, context):
    asyncio.create_task(send_to_remote_logging_service(input_data))
    return {
        "async_": True,
        "asyncTimeout": 30000
    }
```

### 5. Correlate PreToolUse and PostToolUse

Track operations from start to finish:

```python
operations = {}

async def track_pre(input_data, tool_use_id, context):
    if input_data["hook_event_name"] == "PreToolUse":
        operations[tool_use_id] = {
            "start": datetime.utcnow(),
            "tool": input_data["tool_name"]
        }
    return {}

async def track_post(input_data, tool_use_id, context):
    if input_data["hook_event_name"] == "PostToolUse":
        if tool_use_id in operations:
            duration = datetime.utcnow() - operations[tool_use_id]["start"]
            print(f"Tool {input_data['tool_name']} took {duration}")
    return {}
```

### 6. Document Custom Matchers

Make regex patterns clear:

```python
# ❌ Unclear
HookMatcher(matcher="^mcp__|Write|Edit|Delete", hooks=[...])

# ✅ Clear
HookMatcher(
    # Match all MCP tools (mcp__*) and file modification tools
    matcher="^mcp__|Write|Edit|Delete",
    hooks=[...]
)
```

### 7. Set Appropriate Timeouts

Balance between responsiveness and reliability:

```python
# Quick validation: short timeout
HookMatcher(
    matcher="Bash",
    timeout=10,  # 10 seconds
    hooks=[validate_command]
)

# External API call: longer timeout
HookMatcher(
    matcher="Bash",
    timeout=60,  # 60 seconds
    hooks=[external_authorization]
)
```

### 8. Test Hooks Thoroughly

Test both allow and deny paths:

```python
import pytest

async def test_blocks_dangerous_commands():
    result = await protect_destructive_commands(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"}
        },
        "tool_123",
        {}
    )

    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

async def test_allows_safe_commands():
    result = await protect_destructive_commands(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"}
        },
        "tool_123",
        {}
    )

    assert result == {}
```

### 9. Log Hook Decisions

Make debugging easier:

```python
async def log_decision(input_data, tool_use_id, context):
    decision = ...  # Your logic

    print(f"[HOOK] Event: {input_data['hook_event_name']}")
    print(f"[HOOK] Tool: {input_data['tool_name']}")
    print(f"[HOOK] Decision: {decision['hookSpecificOutput']['permissionDecision']}")

    return decision
```

### 10. Use Type Hints (TypeScript)

Make callback signatures clear:

```typescript
import { HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

const validateCommand: HookCallback = async (
  input: PreToolUseHookInput,
  toolUseID: string | undefined,
  { signal }: { signal: AbortSignal }
): Promise<HookOutput> => {
  // ...
};
```

---

## Troubleshooting Guide

### Hook Not Firing

**Symptoms**: Hook callback never executes even though it should

**Diagnosis Checklist**:
1. ✅ Hook event name is correct and case-sensitive (`PreToolUse`, not `preToolUse`)
2. ✅ Hook is in the correct options object
3. ✅ Matcher pattern matches the tool name exactly (use regex tester)
4. ✅ Hook hasn't exceeded its `timeout` value
5. ✅ Agent hasn't hit `max_turns` limit
6. ✅ Hook is registered before calling SDK methods

**Solutions**:

```python
# Debug: Add a hook with no matcher to see all events
async def debug_all_events(input_data, tool_use_id, context):
    print(f"[DEBUG] Event: {input_data['hook_event_name']}")
    print(f"[DEBUG] Tool: {input_data.get('tool_name')}")
    return {}

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[debug_all_events])]  # No matcher
    }
)
```

### Matcher Not Filtering as Expected

**Symptoms**: Hook fires for tools it shouldn't, or doesn't fire for matching tools

**Common Cause**: Matchers only filter by **tool name**, not by arguments

**Solution**: Check arguments inside your callback:

```python
async def my_hook(input_data, tool_use_id, context):
    tool_input = input_data["tool_input"]
    file_path = tool_input.get("file_path", "")

    # Check file path inside callback, not in matcher
    if not file_path.endswith(".md"):
        return {}

    # Process markdown files only
    return {}
```

### Hook Timeout Errors

**Symptoms**: Hook stops executing midway or takes too long

**Solutions**:
1. Increase timeout value
2. Avoid blocking operations (use async)
3. Optimize slow operations

```python
# Solution 1: Increase timeout
HookMatcher(
    matcher="Bash",
    timeout=120,  # 2 minutes instead of 60 seconds
    hooks=[slow_validation]
)

# Solution 2: Use async for slow operations
async def slow_operation(input_data, tool_use_id, context):
    asyncio.create_task(slow_api_call(input_data))
    return {"async_": True, "asyncTimeout": 60000}
```

### Tool Blocked Unexpectedly

**Symptoms**: Valid operation is denied

**Diagnosis**:
1. Check all `PreToolUse` hooks for `deny` decisions
2. Check matcher patterns don't overlap
3. Check `permissionDecisionReason` in logs

**Solution**: Add logging to identify which hook is blocking:

```python
async def my_hook(input_data, tool_use_id, context):
    if should_block:
        print(f"[HOOK] Blocking {input_data['tool_name']}: reason")
        return {
            "hookSpecificOutput": {
                "hookEventName": input_data["hook_event_name"],
                "permissionDecision": "deny",
                "permissionDecisionReason": "reason"  # Include clear reason
            }
        }
    return {}
```

### Input Modification Not Applied

**Symptoms**: Hook returns `updatedInput` but tool still uses original input

**Common Causes**:
1. Missing `permissionDecision: "allow"`
2. `updatedInput` at wrong level (should be inside `hookSpecificOutput`)
3. Mutating original instead of copying

**Solutions**:

```python
# ❌ Wrong: updatedInput at top level
return {
    "updatedInput": {  # Wrong location!
        "file_path": "/new/path"
    }
}

# ✅ Correct: updatedInput inside hookSpecificOutput
return {
    "hookSpecificOutput": {
        "hookEventName": input_data["hook_event_name"],
        "permissionDecision": "allow",  # Must have allow!
        "updatedInput": {
            **input_data["tool_input"],  # Copy original
            "file_path": "/new/path"
        }
    }
}
```

### Session Hooks Not Available in Python

**Symptoms**: `SessionStart` and `SessionEnd` hooks don't work in Python SDK

**Reason**: Only available in TypeScript SDK

**Solutions**:
1. Use `setting_sources` to load shell command hooks from `.claude/settings.json`
2. Use first message from `client.receive_response()` as trigger
3. Use `Stop` hook instead

```python
# Solution 1: Load shell command hooks
options = ClaudeAgentOptions(
    setting_sources=["project"]
)

# Solution 2: Trigger on first message
async def main():
    options = ClaudeAgentOptions()
    async with ClaudeSDKClient(options=options) as client:
        await client.query("start")
        async for message in client.receive_response():
            if first_message:
                # Initialize here
                first_message = False
            print(message)

# Solution 3: Use Stop hook for cleanup
options = ClaudeAgentOptions(
    hooks={"Stop": [HookMatcher(hooks=[cleanup_on_stop])]}
)
```

### Subagent Permission Prompts Multiplying

**Symptoms**: Each subagent asks for permission separately

**Reason**: Subagents don't inherit parent permissions

**Solution**: Auto-approve specific tools for subagents:

```python
async def auto_approve_for_subagents(input_data, tool_use_id, context):
    # Check if running in subagent
    agent_id = input_data.get("agent_id")

    if agent_id and input_data.get("agent_type"):
        # Auto-approve read-only tools in subagents
        read_only = ["Read", "Glob", "Grep"]
        if input_data["tool_name"] in read_only:
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "allow",
                    "permissionDecisionReason": "Auto-approved in subagent"
                }
            }

    return {}
```

### Recursive Hook Loops with Subagents

**Symptoms**: Hook spawns subagent which triggers same hook infinitely

**Solution**: Check for subagent context:

```python
async def check_recursion(input_data, tool_use_id, context):
    # Skip if already in subagent
    if input_data.get("agent_id"):
        return {}

    # Only run for top-level agent
    # Your logic here
    return {}
```

### systemMessage Not Appearing

**Symptoms**: Hook returns `systemMessage` but it doesn't appear in output

**Explanation**: `systemMessage` adds context visible to the model, but may not appear in all output modes

**Solution**: Log messages separately if you need visibility:

```python
async def my_hook(input_data, tool_use_id, context):
    message = "Important context"
    print(f"[CONTEXT] {message}")  # Log for visibility

    return {
        "systemMessage": message  # Also inject into conversation
    }
```

---

## Advanced Topics

### Custom Hook Factories

Create reusable hook generators:

```python
def create_file_protector(protected_paths):
    """Factory function to create file protection hooks."""

    async def protect_files(input_data, tool_use_id, context):
        if input_data["tool_name"] in ["Write", "Edit", "Delete"]:
            file_path = input_data["tool_input"].get("file_path", "")

            if any(file_path.startswith(p) for p in protected_paths):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": input_data["hook_event_name"],
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Protected path"
                    }
                }

        return {}

    return protect_files

# Usage
protect_system = create_file_protector(["/etc", "/sys", "/proc"])
protect_secrets = create_file_protector([".env", ".aws/credentials"])

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Write|Edit|Delete", hooks=[protect_system]),
            HookMatcher(matcher="Write|Edit|Delete", hooks=[protect_secrets])
        ]
    }
)
```

### Hook Middleware Pattern

Chain hooks through middleware:

```python
class HookMiddleware:
    def __init__(self, hooks_list):
        self.hooks = hooks_list

    async def __call__(self, input_data, tool_use_id, context):
        result = {}

        for hook in self.hooks:
            hook_result = await hook(input_data, tool_use_id, context)

            # Merge results (deny takes priority)
            if self._is_deny(hook_result):
                return hook_result

            result = self._merge_results(result, hook_result)

        return result

    def _is_deny(self, result):
        return result.get("hookSpecificOutput", {}).get("permissionDecision") == "deny"

    def _merge_results(self, a, b):
        # Merge logic
        return {**a, **b}

# Usage
middleware = HookMiddleware([validate, transform, log])

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[middleware])]
    }
)
```

### Hook State Management

Maintain state across hook calls:

```python
class HookState:
    def __init__(self):
        self.operations_count = 0
        self.failed_operations = []
        self.last_error = None

    async def count_operation(self, input_data, tool_use_id, context):
        if input_data["hook_event_name"] == "PostToolUse":
            self.operations_count += 1

        return {}

    async def track_failure(self, input_data, tool_use_id, context):
        if input_data["hook_event_name"] == "PostToolUseFailure":
            self.failed_operations.append({
                "tool": input_data["tool_name"],
                "error": input_data.get("error")
            })
            self.last_error = input_data.get("error")

        return {}

    def get_stats(self):
        return {
            "total": self.operations_count,
            "failed": len(self.failed_operations),
            "last_error": self.last_error
        }

# Usage
state = HookState()

options = ClaudeAgentOptions(
    hooks={
        "PostToolUse": [HookMatcher(hooks=[state.count_operation])],
        "PostToolUseFailure": [HookMatcher(hooks=[state.track_failure])]
    }
)

# Later, access stats
print(state.get_stats())
```

### Hook Interceptor Pattern

Intercept and transform all tool calls:

```python
class HookInterceptor:
    def __init__(self):
        self.transforms = {}
        self.validators = []

    def register_transform(self, tool_name, transform_func):
        self.transforms[tool_name] = transform_func

    def register_validator(self, validator_func):
        self.validators.append(validator_func)

    async def intercept(self, input_data, tool_use_id, context):
        if input_data["hook_event_name"] != "PreToolUse":
            return {}

        # Run validators
        for validator in self.validators:
            if not await validator(input_data):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": input_data["hook_event_name"],
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Validation failed"
                    }
                }

        # Run transforms
        tool_name = input_data["tool_name"]
        if tool_name in self.transforms:
            transform = self.transforms[tool_name]
            updated_input = await transform(input_data["tool_input"])

            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "allow",
                    "updatedInput": updated_input
                }
            }

        return {}

# Usage
interceptor = HookInterceptor()

# Register transformations
async def sandbox_writes(tool_input):
    return {
        **tool_input,
        "file_path": f"/sandbox{tool_input['file_path']}"
    }

interceptor.register_transform("Write", sandbox_writes)

# Register validators
async def validate_command(input_data):
    cmd = input_data.get("tool_input", {}).get("command", "")
    return "dangerous" not in cmd.lower()

interceptor.register_validator(validate_command)
```

### Integration with External Systems

Connect hooks to external services:

```python
import aioredis

class ExternalSystemHook:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.create_redis_pool('redis://localhost')

    async def disconnect(self):
        self.redis.close()
        await self.redis.wait_closed()

    async def check_external_policy(self, input_data, tool_use_id, context):
        """Check external policy store (Redis) before allowing operation."""

        if input_data["hook_event_name"] != "PreToolUse":
            return {}

        session_id = input_data["session_id"]
        tool_name = input_data["tool_name"]

        # Check Redis for policy
        key = f"policy:{session_id}:{tool_name}"
        policy = await self.redis.get(key)

        if policy == b"deny":
            return {
                "hookSpecificOutput": {
                    "hookEventName": input_data["hook_event_name"],
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "Policy check failed"
                }
            }

        return {}

# Usage
external_hook = ExternalSystemHook()

await external_hook.connect()

options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(hooks=[external_hook.check_external_policy])]
    }
)

# ... use SDK ...

await external_hook.disconnect()
```

---

## Conclusion

Hooks are a powerful mechanism for implementing behavior-first agent architectures. They enable:

- **Fine-grained control** over agent behavior at each execution point
- **Integration** with external systems and policies
- **Compliance** through comprehensive logging and auditing
- **Security** through validation and blocking mechanisms
- **Customization** of agent behavior for specific use cases

Use this guide as a comprehensive reference when designing and implementing hooks for your agent-based systems.

---

**Quick Reference Checklist**:
- [ ] Define hook event type (PreToolUse, PostToolUse, etc.)
- [ ] Set up matcher pattern if filtering needed
- [ ] Write callback function
- [ ] Handle inputs appropriately
- [ ] Return proper output structure
- [ ] Test allow and deny paths
- [ ] Handle errors gracefully
- [ ] Set appropriate timeout
- [ ] Document your hooks
- [ ] Monitor hook performance

