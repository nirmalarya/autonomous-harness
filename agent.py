"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project


# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    print("Sending prompt to Claude Agent SDK...\n")

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        print(f"\n[Tool: {block.name}]", flush=True)
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                print(f"   Input: {input_str[:200]}...", flush=True)
                            else:
                                print(f"   Input: {input_str}", flush=True)

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            print(f"   [BLOCKED] {result_content}", flush=True)
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            print(f"   [Error] {error_str}", flush=True)
                        else:
                            # Tool succeeded - just show brief confirmation
                            print("   [Done]", flush=True)

        print("\n" + "-" * 70 + "\n")
        return "continue", response_text

    except Exception as e:
        print(f"Error during agent session: {e}")
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
    mode: str = "greenfield",
    spec_file: Optional[str] = None,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        mode: Development mode (greenfield, enhancement, bugfix)
        spec_file: Path to specification file (required for enhancement/bugfix)
    """
    print("\n" + "=" * 70)
    print("  AUTONOMOUS CODING AGENT")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print(f"Model: {model}")
    print(f"Mode: {mode}")
    if spec_file:
        print(f"Spec file: {spec_file}")
    if max_iterations:
        print(f"Max iterations: {max_iterations}")
    else:
        print("Max iterations: Unlimited (will run until completion)")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    spec_dir = project_dir / "spec"
    tests_file = spec_dir / "feature_list.json"
    enhancement_spec_file = spec_dir / "enhancement_spec.txt"
    
    # Determine if this is the first run
    if mode in ["enhancement", "bugfix"]:
        # Enhancement mode: first run if no enhancement_spec.txt exists
        is_first_run = not enhancement_spec_file.exists()
    else:
        # Greenfield mode: first run if no feature_list.json exists
        is_first_run = not tests_file.exists()

    if is_first_run:
        print(f"🆕 Fresh start - will use initializer agent ({mode} mode)")
        print()
        if mode == "greenfield":
            print("=" * 70)
            print("  NOTE: First session takes 10-20+ minutes!")
            print("  The agent is generating 100+ detailed test cases.")
            print("  This may appear to hang - it's working. Watch for [Tool: ...] output.")
            print("=" * 70)
        else:
            print("=" * 70)
            print(f"  {mode.upper()} MODE - Enhancing existing project")
            print("  Reading existing feature_list.json and appending new features.")
            print("=" * 70)
        print()
        # Copy the spec into the project directory for the agent to read
        copy_spec_to_project(project_dir, spec_file, mode)
    else:
        print(f"Continuing existing project ({mode} mode)")
        print_progress_summary(project_dir)

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break
        
        # Check if project is 100% complete (CRITICAL!)
        spec_feature_list = spec_dir / "feature_list.json"
        if spec_feature_list.exists():
            import json
            try:
                with open(spec_feature_list) as f:
                    features = json.load(f)
                total = len(features)
                passing = sum(1 for f in features if f.get('passes', False))
                
                if passing >= total and total > 0:
                    print("\n" + "=" * 70)
                    print(f"🎉 PROJECT 100% COMPLETE ({passing}/{total} features passing)!")
                    print("=" * 70)
                    print("\nAll features are marked as passing.")
                    print("The autonomous coding work is DONE.")
                    print("\n✅ STOPPING AUTOMATICALLY - No further work needed!")
                    print("\nTo add more features, create a new enhancement spec.")
                    print("=" * 70)
                    return  # Exit the function, stopping the loop
            except (json.JSONDecodeError, IOError):
                pass  # Continue if we can't read the file

        # Print session header
        print_session_header(iteration, is_first_run)

        # Create client (fresh context)
        client = create_client(project_dir, model)

        # Choose prompt based on session type and mode
        if is_first_run:
            prompt = get_initializer_prompt(mode)
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt(mode)

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(client, prompt, project_dir)

        # Handle status
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            print("\nSession encountered an error")
            print("Will retry with a fresh session...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            print("\nPreparing next session...\n")
            await asyncio.sleep(1)

    # Final summary
    print("\n" + "=" * 70)
    print("  SESSION COMPLETE")
    print("=" * 70)
    print(f"\nProject directory: {project_dir}")
    print_progress_summary(project_dir)

    # Print instructions for running the generated application
    print("\n" + "-" * 70)
    print("  TO RUN THE GENERATED APPLICATION:")
    print("-" * 70)
    print(f"\n  cd {project_dir.resolve()}")
    print("  ./init.sh           # Run the setup script")
    print("  # Or manually:")
    print("  npm install && npm run dev")
    print("\n  Then open http://localhost:3000 (or check init.sh for the URL)")
    print("-" * 70)

    print("\nDone!")
