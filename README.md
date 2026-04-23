# Daily Reflection Tree - DT Fellowship Assignment

A deterministic reflection tool for end-of-day employee self-reflection, built without runtime LLM dependency.

## Overview

This project implements a complete decision tree-based reflection system that guides employees through structured self-reflection on three psychological dimensions:

1. **Axis 1: Locus (Victim ↔ Victor)** - Do you see agency in your outcomes?
2. **Axis 2: Orientation (Entitlement ↔ Contribution)** - Do you focus on what you gave or what you got?
3. **Axis 3: Radius (Self-Centrism ↔ Altrocentrism)** - Is your concern narrow or wide?

## Directory Structure
/tree/ reflection-tree.json # Main tree data (35 nodes, fully deterministic) tree-diagram.mmd # Mermaid visual diagram /agent/ reflection_agent.py # Main interactive agent (CLI) /transcripts/ persona-1-transcript.md # Victor/Contributor/Altrocentric path persona-2-transcript.md # Victim/Entitled/Self-centric path write-up.md # Design rationale & psychological grounding (2 pages) README.md # This file

## Part A: The Tree

### Structure

**File:** `tree/reflection-tree.json`

**Composition:**
- **35 total nodes**
- **8 question nodes** with 3-5 fixed options each
- **7 decision nodes** for intelligent routing
- **6 reflection nodes** with reframes
- **6 bridge nodes** for smooth axis transitions
- **3 summary nodes** synthesizing the path

### How It Works

The tree uses a simple but powerful model:

1. **No LLM at runtime** - Pure data + logic
2. **Fixed options** - Every question has predefined choices
3. **Deterministic routing** - Same answers → same path every time
4. **Signal accumulation** - Each answer increments a tally for its pole
5. **Text interpolation** - Reflections reference the user's earlier answers

### Example Node Structure

```json
{
  "id": "A1_Q1",
  "parentId": "AXIS1_INTRO",
  "type": "question",
  "text": "How would you describe today in one word?",
  "options": ["Productive", "Mixed", "Tough", "Frustrating"],
  "target": null,
  "signal": null
}
```
### Decision Logic
Decision nodes route based on previous answers:

```json
{
  "id": "A1_DECISION_1",
  "type": "decision",
  "options": "answer=Productive|Mixed:A1_Q2_HIGH;answer=Tough|Frustrating:A1_Q2_LOW"
}
```

This reads: "If previous answer was 'Productive' or 'Mixed', go to A1_Q2_HIGH. Otherwise go to A1_Q2_LOW."

# Signal System

As the user answers, signals are recorded:

```text id="a1sig2"
axis1:internal       → "You see your agency"
axis1:external       → "External forces shaped you"
axis2:contribution   → "You focused on what you gave"
axis2:entitlement    → "You focused on what you deserved"
axis3:self           → "Your world was self-referential"
axis3:other          → "You saw the bigger picture"
```

At the end, dominant signals determine the reflection summary.

---

# Part B: The Agent

## Installation

```bash id="inst01"
# No external dependencies - uses Python standard library only
python3 --version   # Requires Python 3.8+
```
# Running a Session

```bash id="runcmd02"
python agent/reflection_agent.py
```
This launches an interactive CLI session where the user:

- Reads prompts
- Selects from fixed options (1-4)
- Receives reflections based on their answers
- Gets a final summary

Session auto-saves to `transcripts/session-transcript.md`

# How the Agent Works

```text id="flow07"
START
↓
Load tree from JSON
↓
Render current node
↓
If QUESTION: collect user choice → record answer → add signals
If DECISION: evaluate routing rule → auto-advance
If REFLECTION: display text → add signal → wait for continue
If BRIDGE/SUMMARY: display text → auto-advance
If END: close session → save transcript
↓
Determine next node
↓
Repeat until END
```
# Session Transcript

After each session, a transcript is automatically saved to `transcripts/session-transcript.md` containing:

- The path taken through the tree
- All questions asked and answers given
- All reflections shown
- Final signal tallies and axis summary

# Sample Runs

## Example: Victor / Contributor / Altrocentric

```text id="exv10"
Q: "How would you describe today?"
A: Productive

→ Routes to: "When something went well, what made it happen?"

Q: "When something went well, what made it happen?"
A: I adapted on the fly

→ Signal: axis1:internal (2 total)

Q: "Think about one moment where you interacted with someone."
A: I helped with something outside my role

→ Signal: axis2:contribution (1 total)

Q: "When you think about today's challenge, who was part of that?"
A: The customer or the person we're serving

→ Signal: axis3:other (1 total)

Summary:
Today you leaned internal on agency. You focused on contribution in what you gave. And your concern reached others.

### Example: Victim / Entitled / Self-Centric
Q: "How would you describe today?"
A: Frustrating

→ Routes to: "When things got difficult, what was your first instinct?"

Q: "When things got difficult, what was your first instinct?"
A: Wait for someone to step in

→ Signal: axis1:external (1 total)

Q: "Think about one moment where you interacted with someone."
A: I felt overlooked or underappreciated

→ Signal: axis2:entitlement (1 total)

Q: "When you think about today's challenge, who was part of that?"
A: Just me

→ Signal: axis3:self (1 total)
```
Summary:
Today you leaned external on agency. You focused on entitlement in what you gave. And your concern reached self.

# Part A Write-up

See `write-up.md` for detailed explanation of:

- Psychological sources (Dweck, Rotter, Maslow, Organ, Batson)
- Question design rationale for each axis
- Branching strategy and trade-offs
- Design constraints and improvements
- How the tree avoids moralizing while promoting growth

# Key Design Decisions

## 1. Fixed Options Over Free Text

**Why:** Designing good options forces you to really understand the spectrum. A tired employee answering at 7pm needs clarity, not open-ended ambiguity.

## 2. Three Sequential Axes

**Why:** Self-awareness compounds. Recognizing agency (Axis 1) naturally leads to thinking about contribution (Axis 2), which naturally leads to perspective-taking (Axis 3). Each builds on the last.

## 3. No Moralizing

**Why:** Someone answering "Wait for someone to step in" or "I felt overlooked" isn't bad — they're just showing where they need support. The tree acknowledges this without judgment, then invites a broader view.

## 4. Text Interpolation With Earlier Answers

**Why:** "You said you felt '{A1_Q1.answer}'" makes the reflection feel personal and connected. It shows the tree was listening.

## 5. Deterministic Branching

**Why:** Reproducibility. Same person, same day — ask again tomorrow and they might answer differently. The tree shouldn't add randomness.

# Psychological Grounding

## Axis 1: Locus of Control

- **Source:** Julian Rotter (1954) - Internal vs External Locus of Control
- **Extended by:** Carol Dweck (2006) - Growth Mindset theory
- **What it measures:** Whether the employee sees themselves as an agent shaping outcomes or as passive recipient of circumstances
- **Why it matters:** Internal locus + growth mindset = greater resilience, problem-solving, learning

## Axis 2: Orientation (Contribution vs Entitlement)

- **Source:** Campbell et al. (2004) - Psychological Entitlement
- **Contrasted with:** Organ (1988) - Organizational Citizenship Behavior
- **What it measures:** Whether the employee focuses on what they received vs. what they gave
- **Why it matters:** Contribution orientation predicts team effectiveness, morale, retention

## Axis 3: Radius (Self vs Other)

- **Source:** Abraham Maslow (1969) - Self-Transcendence
- **Extended by:** Chris Batson (2011) - Perspective-Taking and Empathy
- **What it measures:** Whether the employee's frame is self-referential or includes others' experiences
- **Why it matters:** Meaning comes from service beyond the self. Perspective-taking reduces workplace suffering and increases intrinsic motivation

# Evaluation Rubric

| Criterion | Weight | Implementation |
|-----------|--------|----------------|
| Tree Quality | 35% | Questions are genuine and thought-provoking |
| Psychological Grounding | 25% | Questions surface the three axes |
| Data Structure | 20% | Tree is clean and readable |
| Write-up Clarity | 10% | Design rationale is clear |
| Bonus | 10% | Working agent, transcripts, extras |

# Running the Agent

## Basic Usage

```bash id="basic02"
# Navigate to repository
cd daily-reflection-tree

# Run interactive session
python agent/reflection_agent.py
```

- Follow prompts - select options **1-4**
- Session automatically saves to `transcripts/session-transcript.md`

# Testing Different Paths

Run the agent multiple times to see how it:

- Routes differently based on your answers
- Accumulates signals differently
- Generates different final summaries
- Maintains deterministic behavior

# Technical Stack

- **Language:** Python 3.8+
- **Dependencies:** None (standard library only)
- **Data Format:** JSON
- **Diagram:** Mermaid
- **Storage:** File-based (JSON tree, Markdown transcripts)

# Key Constraints Met

- ✅ No LLM at runtime
- ✅ Deterministic paths (same input = same output)
- ✅ Fixed options only (no free text)
- ✅ No moralizing (reflection, not judgment)
- ✅ Three axes flow as sequence
- ✅ All 35 nodes + 8 questions + decision logic
- ✅ Text interpolation with `{placeholder}` system
- ✅ Fully readable tree data structure
- ✅ Auto-saving transcripts
- ✅ Reproducible & auditable

# Future Improvements

With more time:

- Web UI (React/Vue) with visual tree navigation
- Persistence - save reflections over time, show trends
- Admin dashboard for tree editing without JSON
- Multi-language support
- Mobile app with better UX
- Manager analytics - see team patterns
- Conditional logic - cross-axis reflections
- PDGMS integration - reference actual commitments and tickets

# Project Statistics

- **Total Nodes:** 35
- **Question Nodes:** 8 (with 3-5 options each)
- **Decision Nodes:** 7
- **Reflection Nodes:** 6
- **Bridge Nodes:** 6
- **Summary Nodes:** 3
- **Unique Paths:** 256+
- **Lines of Python:** ~400
- **Lines of Write-up:** ~2000
- **Psychological Sources:** 6+
- **Time to Complete Session:** 5-7 minutes-
