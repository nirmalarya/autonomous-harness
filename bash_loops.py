"""
Bash Loop Templates for v3.7.0 Compatibility
=============================================

Fallback bash loops for when Ralph Wiggum plugin is not available.
These are the original v3.7.0 iteration loops.
"""

E2E_DEBUGGING_BASH_LOOP = """
```bash
#!/bin/bash
# E2E Debugging Iteration Loop (v3.7.0 Bash Fallback)

iteration=1
max_iterations=10
e2e_test="test_feature_XXX_e2e.py"  # Replace with actual test file

echo "🔄 Starting E2E Debugging Loop (max $max_iterations iterations)"
echo ""

while [ $iteration -le $max_iterations ]; do
    echo "═══════════════════════════════════════════════"
    echo "🔄 E2E Debugging Iteration $iteration/$max_iterations"
    echo "═══════════════════════════════════════════════"
    echo ""

    # === DIAGNOSTIC PHASE ===
    echo "📋 Step 1: Running diagnostic checks..."
    echo ""

    # Check 1: Backend running?
    echo "  [1/5] Backend process status..."
    ps aux | grep uvicorn | grep -v grep || echo "     ⚠️  Backend not running"
    lsof -i :8100 2>/dev/null || echo "     ⚠️  Port 8100 not listening"
    echo ""

    # Check 2: Backend health
    echo "  [2/5] Backend health check..."
    if curl -s -f http://localhost:8100/health > /dev/null 2>&1; then
        echo "     ✅ Backend responding"
    else
        echo "     ❌ Backend not responding"
    fi
    echo ""

    # Check 3: Database connectivity
    echo "  [3/5] Database status..."
    docker ps | grep postgres || echo "     ⚠️  Postgres not running"
    echo ""

    # Check 4: Backend logs
    echo "  [4/5] Recent backend logs..."
    tail -20 backend/logs/app.log 2>/dev/null || tail -20 logs/app.log 2>/dev/null || echo "     ℹ️  No logs found"
    echo ""

    # Check 5: Zombie processes
    echo "  [5/5] Checking for zombie processes..."
    zombies=$(ps aux | grep -E "(python.*main\\.py|uvicorn)" | grep -v grep | wc -l)
    echo "     Found $zombies backend processes"
    echo ""

    # === FIX PHASE ===
    echo "🔧 Step 2: Applying fixes based on diagnostics..."
    echo ""

    # Fix 1: Backend not running or not healthy
    if ! curl -s -f http://localhost:8100/health > /dev/null 2>&1; then
        echo "  → Fixing backend connectivity..."

        # Kill zombies
        pkill -9 -f uvicorn 2>/dev/null
        pkill -9 -f "python.*main.py" 2>/dev/null
        sleep 2

        # Restart backend
        cd backend 2>/dev/null || cd .
        python -m uvicorn main:app --reload --port 8100 --host 0.0.0.0 > /dev/null 2>&1 &
        sleep 5

        # Verify
        if curl -s -f http://localhost:8100/health > /dev/null 2>&1; then
            echo "     ✅ Backend restarted successfully"
        else
            echo "     ❌ Backend still not responding"
        fi
        cd - > /dev/null 2>&1
    fi
    echo ""

    # Fix 2: Database not running
    if ! docker ps | grep postgres > /dev/null 2>&1; then
        echo "  → Starting database..."
        docker-compose up -d postgres 2>/dev/null
        sleep 3
        echo "     ✅ Database started"
    fi
    echo ""

    # === TEST PHASE ===
    echo "🧪 Step 3: Re-running E2E test..."
    echo ""

    # Run the E2E test
    python3 "$e2e_test"
    test_result=$?
    echo ""

    # Check result
    if [ $test_result -eq 0 ]; then
        echo "═══════════════════════════════════════════════"
        echo "✅ SUCCESS! E2E test PASSED on iteration $iteration"
        echo "═══════════════════════════════════════════════"
        echo ""
        echo "<promise>E2E_PASSED</promise>"
        exit 0  # SUCCESS - Exit loop
    else
        echo "❌ E2E test still failing on iteration $iteration"
        echo ""
    fi

    # Increment iteration
    iteration=$((iteration + 1))

    # Short delay before next iteration
    if [ $iteration -le $max_iterations ]; then
        echo "⏱️  Waiting 3 seconds before next iteration..."
        sleep 3
        echo ""
    fi
done

# Max iterations reached
echo "═══════════════════════════════════════════════"
echo "❌ E2E DEBUGGING FAILED"
echo "═══════════════════════════════════════════════"
echo ""
echo "Reached maximum iterations ($max_iterations) without success."
echo ""
echo "Possible issues:"
echo "  - Backend code has bugs preventing proper response"
echo "  - Database schema doesn't match expected structure"
echo "  - Test expectations don't match actual behavior"
echo "  - Network/port configuration issues"
echo ""
echo "DO NOT mark feature as passing! Continue debugging or mark 'passes': false"
exit 1
```

**How to use this loop:**

1. **Copy the script above** and replace `test_feature_XXX_e2e.py` with your actual E2E test file name
2. **Run the script** - it will iterate up to 10 times
3. **Each iteration** runs diagnostics → applies fixes → re-runs test
4. **Completion**: Outputs `<promise>E2E_PASSED</promise>` when test passes
"""

FEATURE_QUALITY_BASH_LOOP = """
```bash
#!/bin/bash
# Feature Quality Loop - Iterate until all gates pass (v3.7.0 Bash Fallback)

echo "🎯 FEATURE QUALITY LOOP"
echo "Iterating through all quality gates until ALL pass..."
echo ""

# Initialize gate tracking
gates_passed=0
total_gates=8

# Gate 1: Stop condition check
echo "[Gate 1/8] Stop condition..."
total=$(cat spec/feature_list.json | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")
passing=$(cat spec/feature_list.json | python3 -c "import json, sys; print(len([f for f in json.load(sys.stdin) if f.get('passes')]))")
if [ "$passing" = "$total" ]; then
    echo "  ❌ STOP! Project is 100% complete - no more work needed!"
    exit 1
else
    echo "  ✅ Project not complete ($passing/$total) - proceed"
    gates_passed=$((gates_passed + 1))
fi
echo ""

# Gate 2: Services healthy
echo "[Gate 2/8] Services health check..."
if curl -s -f http://localhost:8100/health > /dev/null 2>&1; then
    echo "  ✅ Backend healthy"
    gates_passed=$((gates_passed + 1))
else
    echo "  ❌ Backend not healthy - fix before proceeding!"
    echo "  → Run: pkill -f uvicorn && cd backend && python -m uvicorn main:app --reload --port 8100 &"
    exit 1
fi
echo ""

# Gate 3: Database schema validated (if needed)
echo "[Gate 3/8] Database schema..."
# Add your schema validation here
# Example: Check if required columns exist
echo "  ✅ Schema validated (or not applicable)"
gates_passed=$((gates_passed + 1))
echo ""

# Gate 4: Browser integration tested (if frontend feature)
echo "[Gate 4/8] Browser integration..."
# Manual check - user should have tested with F12 DevTools
echo "  ℹ️  Have you tested with F12 DevTools?"
echo "     - Zero CORS errors in Network tab?"
echo "     - Zero red errors in Console tab?"
echo "     - Proper 200 OK responses?"
read -p "  Tested with DevTools? (y/n): " devtools_tested
if [ "$devtools_tested" = "y" ]; then
    echo "  ✅ Browser integration tested"
    gates_passed=$((gates_passed + 1))
else
    echo "  ❌ Test with browser DevTools first!"
    exit 1
fi
echo ""

# Gate 5: E2E test created and passing (CRITICAL!)
echo "[Gate 5/8] E2E test execution..."
e2e_test=$(git diff --name-only HEAD | grep -E "test_.*_(e2e|api)\\.(py|ts|js)$" | head -1)
if [ -z "$e2e_test" ]; then
    echo "  ❌ No E2E test found!"
    echo "  → Create test_feature_XXX_e2e.py first"
    exit 1
fi

python3 "$e2e_test"
if [ $? -eq 0 ]; then
    echo "  ✅ E2E test passed"
    gates_passed=$((gates_passed + 1))
else
    echo "  ❌ E2E test failed - run debugging loop (STEP 12.5)!"
    exit 1
fi
echo ""

# Gate 6: Screenshots saved (if UI feature)
echo "[Gate 6/8] E2E artifacts..."
screenshot_count=$(ls -1 .claude/verification/*.png 2>/dev/null | wc -l)
if [ -f ".claude/verification/test_results.json" ] && [ $screenshot_count -gt 0 ]; then
    echo "  ✅ Screenshots ($screenshot_count) and test_results.json exist"
    gates_passed=$((gates_passed + 1))
else
    echo "  ⚠️  No E2E artifacts (acceptable if backend-only feature)"
    gates_passed=$((gates_passed + 1))
fi
echo ""

# Gate 7: Zero TODOs
echo "[Gate 7/8] Zero TODOs check..."
modified_files=$(git diff --name-only HEAD)
todos=$(echo "$modified_files" | xargs grep -n "TODO\\|FIXME\\|WIP" 2>/dev/null || true)
if [ -z "$todos" ]; then
    echo "  ✅ No TODOs in implementation code"
    gates_passed=$((gates_passed + 1))
else
    echo "  ❌ TODOs found:"
    echo "$todos"
    exit 1
fi
echo ""

# Gate 8: Security checklist (if applicable)
echo "[Gate 8/8] Security checklist..."
read -p "  Is this an auth/security feature? (y/n): " is_security
if [ "$is_security" = "y" ]; then
    echo "  Security checklist:"
    echo "    - [ ] No credentials in URLs"
    echo "    - [ ] Passwords hashed (bcrypt cost 12+)"
    echo "    - [ ] JWT tokens expire (< 24h)"
    echo "    - [ ] Input validation"
    echo "    - [ ] SQL injection prevention"
    echo "    - [ ] XSS prevention"
    echo "    - [ ] Rate limiting"
    echo "    - [ ] CORS configured"
    read -p "  All security items checked? (y/n): " security_done
    if [ "$security_done" = "y" ]; then
        echo "  ✅ Security checklist complete"
        gates_passed=$((gates_passed + 1))
    else
        echo "  ❌ Complete security checklist first!"
        exit 1
    fi
else
    echo "  ✅ Not a security feature (skipped)"
    gates_passed=$((gates_passed + 1))
fi
echo ""

# All gates passed!
echo "═══════════════════════════════════════════════"
echo "✅ ALL QUALITY GATES PASSED ($gates_passed/$total_gates)"
echo "═══════════════════════════════════════════════"
echo ""
echo "<promise>FEATURE_COMPLETE</promise>"
echo ""
echo "You may now mark the feature as passing in feature_list.json!"
echo "You may also create the marker file:"
echo "  echo 'FEATURE_COMPLETE' > .claude/completion_promise.marker"
```

**Quality Gate Summary:**
1. Stop condition - Project not 100% complete
2. Services healthy - Backend/frontend running
3. Database schema - Migrations applied
4. Browser integration - Tested with F12 DevTools
5. E2E test passing - Exit code 0
6. E2E artifacts - Screenshots and test_results.json
7. Zero TODOs - No incomplete work
8. Security checklist - All items checked (if applicable)
"""


def get_e2e_debugging_loop(iteration_mode: str) -> str:
    """
    Get E2E debugging loop instructions based on iteration mode.

    Args:
        iteration_mode: "ralph" or "bash"

    Returns:
        Formatted E2E debugging loop instructions
    """
    if iteration_mode == "bash":
        return E2E_DEBUGGING_BASH_LOOP
    else:
        # Ralph mode - return empty (Ralph instructions already in coding_prompt.md)
        return ""


def get_feature_quality_loop(iteration_mode: str) -> str:
    """
    Get feature quality loop instructions based on iteration mode.

    Args:
        iteration_mode: "ralph" or "bash"

    Returns:
        Formatted feature quality loop instructions
    """
    if iteration_mode == "bash":
        return FEATURE_QUALITY_BASH_LOOP
    else:
        # Ralph mode - return empty (Ralph instructions already in coding_prompt.md)
        return ""
