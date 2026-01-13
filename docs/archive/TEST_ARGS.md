# ✅ FIXED - Ready to Run!

## Updated `autonomous_agent.py`

Added support for:
- `--mode` (greenfield, enhancement, bugfix)
- `--spec` (path to spec file)

## Usage

### Greenfield (New Project)
```bash
python3 autonomous_agent.py \
  --project-dir ./my-new-project \
  --mode greenfield \
  --spec specs/simple_todo_spec.txt
```

### Enhancement Mode (AutoGraph)
```bash
python3 autonomous_agent.py \
  --project-dir /Users/nirmalarya/Workspace/autograph \
  --mode enhancement \
  --spec specs/autograph_bugfix_spec.txt \
  --max-iterations 50
```

### Bugfix Mode (SHERPA)
```bash
python3 autonomous_agent.py \
  --project-dir /Users/nirmalarya/Workspace/sherpa \
  --mode bugfix \
  --spec specs/sherpa_enhancement_spec.txt
```

## ✅ Ready to Test!

Try running:
```bash
python3 autonomous_agent.py --help
```

Should show all the new arguments!

