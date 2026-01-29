"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.

v3.1.0 enhancements:
- Triple timeout protection (15-min no-response, 10-min stall, 120-min session)
- Retry + skip logic (auto-recovery from failures)
- Comprehensive error handling and logging
"""

import asyncio
import json
from pathlib import Path

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from error_handler import ErrorHandler
from loop_detector import LoopDetector
from output_formatter import format_tool_output
from progress import print_progress_summary, print_session_header
from prompts import copy_spec_to_project, get_coding_prompt, get_initializer_prompt
from retry_manager import RetryManager

# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
    loop_detector: LoopDetector | None = None,
    error_handler: ErrorHandler | None = None,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path
        loop_detector: Loop detector for timeout/loop detection
        error_handler: Error handler for logging

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "timeout" if session timed out or stalled
        - "error" if an error occurred
    """
    print("Sending prompt to Claude Agent SDK...\n")

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            # Check for timeout/loop before processing message
            if loop_detector:
                is_stuck, reason = loop_detector.check()
                if is_stuck:
                    print(f"\n🛑 Session stopped: {reason}\n")
                    if error_handler:
                        error_handler.record_warning("session_timeout", reason)
                    return "timeout", response_text

            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        tool_name = block.name
                        tool_input = block.input if hasattr(block, "input") else {}

                        # Track tool use for loop detection
                        if loop_detector:
                            # Determine tool type
                            if tool_name in ["read_file", "cat", "head", "tail"]:
                                file_path = tool_input.get("file_path", tool_input.get("path", ""))
                                loop_detector.track_tool("read", file_path)
                            else:
                                loop_detector.track_tool(tool_name)

                        try:
                            formatted = format_tool_output(tool_name, tool_input)
                            print(formatted, flush=True)
                        except Exception:
                            # Fallback to simple output if formatter fails
                            print(f"\n[Tool: {tool_name}]", flush=True)
                            input_str = str(tool_input)
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
        if error_handler:
            error_handler.record_error("agent_session", e, fatal=False)
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: int | None = None,
    mode: str = "greenfield",
    spec_file: str | None = None,
    session_timeout_minutes: int = 120,
    stall_timeout_minutes: int = 10,
    max_retries: int = 3,
    iteration_mode: str = "ralph",
) -> None:
    """
    Run the autonomous agent loop with production reliability features.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        mode: Development mode (greenfield, enhancement, bugfix)
        spec_file: Path to specification file (required for enhancement/bugfix)
        session_timeout_minutes: Overall session timeout (default: 120 min)
        stall_timeout_minutes: No-activity timeout (default: 10 min)
        max_retries: Max retry attempts per feature (default: 3)
        iteration_mode: Iteration mode - "ralph" (Ralph plugin) or "bash" (v3.7.0 loops)
    """
    # Read version
    try:
        version_file = Path(__file__).parent / "VERSION"
        version = version_file.read_text().strip()
    except Exception:
        from version import __version__

        version = __version__

    print("\n" + "=" * 70)
    print(f"  AUTONOMOUS CODING AGENT v{version}")
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

    # Show reliability features
    print("\n📊 Reliability Features:")
    print(f"   Session timeout: {session_timeout_minutes} min")
    print(f"   Stall timeout: {stall_timeout_minutes} min")
    print("   No-response timeout: 15 min")
    print(f"   Max retries per feature: {max_retries}")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Initialize reliability components
    retry_manager = RetryManager(project_dir, max_retries=max_retries)
    error_handler = ErrorHandler(project_dir)
    loop_detector = LoopDetector(
        session_timeout_minutes=session_timeout_minutes, stall_timeout_minutes=stall_timeout_minutes
    )

    print("✅ Reliability components initialized\n")

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

    def get_current_feature(features: list, retry_mgr: RetryManager) -> dict | None:
        """
        Get the next feature to work on, prioritizing by retry count.
        
        Strategy: Work on features with fewer failures first, but never skip.
        This way easier features get done while harder ones keep getting retried.
        """
        incomplete = []
        for feature in features:
            if feature.get("passes", False):
                continue  # Already complete
            feature_id = feature.get("id") or feature.get("description", "")[:50]
            retry_count = retry_mgr.get_retry_count(feature_id)
            incomplete.append((retry_count, feature))
        
        if not incomplete:
            return None
        
        # Sort by retry count (fewer failures first) to prioritize easier features
        incomplete.sort(key=lambda x: x[0])
        return incomplete[0][1]

    def get_feature_id(feature: dict) -> str:
        """Extract a unique identifier for a feature."""
        return feature.get("id") or feature.get("description", "unknown")[:50]

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            print(f"\nReached max iterations ({max_iterations})")
            print("To continue, run the script again without --max-iterations")
            break

        # Check if project is 100% complete (CRITICAL!)
        # BUT: Skip this check on iteration 1 for enhancement/bugfix mode
        #      (let initializer add new features first!)
        spec_feature_list = spec_dir / "feature_list.json"

        # Track current feature for retry logic
        current_feature = None
        current_feature_id = None
        features_before = []

        if (
            iteration > 1 or mode == "greenfield"
        ):  # Only check after first session, or always in greenfield
            if spec_feature_list.exists():
                try:
                    with open(spec_feature_list) as f:
                        features_before = json.load(f)
                    total = len(features_before)
                    passing = sum(1 for f in features_before if f.get("passes", False))

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

                    # Identify current feature for retry tracking (prioritizes fewer failures)
                    current_feature = get_current_feature(features_before, retry_manager)
                    if current_feature:
                        current_feature_id = get_feature_id(current_feature)
                        retry_count = retry_manager.get_retry_count(current_feature_id)
                        if retry_count >= max_retries:
                            print(f"⚠️  Feature struggling ({retry_count} attempts): {current_feature_id[:50]}...")
                            print("   Will keep trying - consider manual review if this persists")
                        elif retry_count > 0:
                            print(f"📋 Resuming feature: {current_feature_id[:60]}... (attempt {retry_count + 1})")
                        else:
                            print(f"📋 Working on feature: {current_feature_id[:60]}...")

                except (OSError, json.JSONDecodeError):
                    pass  # Continue if we can't read the file

        # Print session header
        print_session_header(iteration, is_first_run)

        # Create client (fresh context) with mode-specific MCP servers
        client = create_client(project_dir, model, mode)

        # Choose prompt based on session type and mode
        if is_first_run:
            prompt = get_initializer_prompt(mode)
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt(mode)

        # Reset loop detector for fresh session
        loop_detector.reset()

        # Run session with async context manager
        async with client:
            status, response = await run_agent_session(
                client,
                prompt,
                project_dir,
                loop_detector=loop_detector,
                error_handler=error_handler,
            )

        # Handle status with retry tracking
        if status == "continue":
            print(f"\nAgent will auto-continue in {AUTO_CONTINUE_DELAY_SECONDS}s...")
            print_progress_summary(project_dir)

            # Check if current feature was completed (passes changed to true)
            if current_feature_id and spec_feature_list.exists():
                try:
                    with open(spec_feature_list) as f:
                        features_after = json.load(f)
                    for feature in features_after:
                        fid = get_feature_id(feature)
                        if fid == current_feature_id and feature.get("passes", False):
                            retry_manager.record_success(current_feature_id)
                            print(f"✅ Feature completed: {current_feature_id[:60]}...")
                            break
                except (OSError, json.JSONDecodeError):
                    pass

            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "timeout":
            print("\n🛑 Session timed out or stalled")
            # Record timeout for tracking (used to prioritize easier features first)
            if current_feature_id:
                retry_manager.record_failure(current_feature_id, "Session timeout/stall")
                retry_count = retry_manager.get_retry_count(current_feature_id)
                print(f"🔄 Will retry feature (attempt {retry_count} recorded)")
                if retry_count >= max_retries:
                    print(f"   ⚠️  This feature has failed {retry_count} times - may need manual review")
            print("Retrying with fresh context...")
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

        elif status == "error":
            print("\n❌ Session encountered an error")
            # Record error for tracking (used to prioritize easier features first)
            if current_feature_id:
                retry_manager.record_failure(current_feature_id, f"Session error: {response[:100]}")
                retry_count = retry_manager.get_retry_count(current_feature_id)
                print(f"🔄 Will retry feature (attempt {retry_count} recorded)")
                if retry_count >= max_retries:
                    print(f"   ⚠️  This feature has failed {retry_count} times - may need manual review")
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

    # Print retry/error statistics
    retry_stats = retry_manager.get_stats()
    if retry_stats["features_being_retried"] > 0:
        print("\n" + "=" * 70)
        print("  RETRY STATISTICS")
        print("=" * 70)
        print(f"\nFeatures with recorded failures: {retry_stats['features_being_retried']}")
        print(f"Total retry attempts: {retry_stats['total_retry_attempts']}")
        
        # Show features that are struggling (many failures)
        struggling = [(fid, count) for fid, count in retry_stats.get("retry_count", {}).items() 
                      if count >= max_retries]
        if struggling:
            print(f"\n⚠️  Features needing attention ({len(struggling)}):")
            for feature_id, count in struggling:
                print(f"   - {feature_id[:50]}... ({count} failures)")
            print("\n   These features keep failing - consider manual review")
        print("=" * 70)

    # Print error summary
    error_handler.print_session_summary()

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

    print("\n✅ Done!")
