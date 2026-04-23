#!/usr/bin/env python3
"""
Daily Reflection Tree - Interactive Agent
A deterministic reflection tool that walks employees through guided self-reflection.
"""

import json
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum


class NodeType(Enum):
    START = "start"
    QUESTION = "question"
    DECISION = "decision"
    REFLECTION = "reflection"
    BRIDGE = "bridge"
    SUMMARY = "summary"
    END = "end"


class TreeLoader:
    """Load and parse the reflection tree from JSON."""
    
    @staticmethod
    def load(filepath: str) -> Dict:
        """Load tree from JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_node(tree: Dict, node_id: str) -> Optional[Dict]:
        """Get a node by ID."""
        for node in tree['nodes']:
            if node['id'] == node_id:
                return node
        return None


class StateManager:
    """Manage session state - answers, signals, and path history."""
    
    def __init__(self):
        self.answers: Dict[str, str] = {}
        self.signals: Dict[str, Dict[str, int]] = {
            'axis1': {'internal': 0, 'external': 0},
            'axis2': {'contribution': 0, 'entitlement': 0},
            'axis3': {'self': 0, 'other': 0}
        }
        self.path: List[str] = []
    
    def record_answer(self, node_id: str, answer: str):
        """Record user's answer to a question."""
        self.answers[node_id] = answer
    
    def add_signal(self, signal: str):
        """Add a signal to tally."""
        if not signal:
            return
        
        parts = signal.split(':')
        if len(parts) == 2:
            axis, pole = parts
            if axis in self.signals and pole in self.signals[axis]:
                self.signals[axis][pole] += 1
    
    def record_path(self, node_id: str):
        """Record the path taken through the tree."""
        self.path.append(node_id)
    
    def get_dominant_pole(self, axis: str) -> str:
        """Get the dominant pole for an axis."""
        if axis not in self.signals:
            return "neutral"
        
        poles = self.signals[axis]
        if poles['internal'] > poles['external']:
            return "internal (you see your agency)"
        elif poles['external'] > poles['internal']:
            return "external (circumstances shaped you)"
        else:
            return "balanced"
        # Similar for other axes
        if 'contribution' in poles and 'entitlement' in poles:
            if poles['contribution'] > poles['entitlement']:
                return "contribution (what you gave)"
            elif poles['entitlement'] > poles['contribution']:
                return "entitlement (what you deserved)"
        
        if 'self' in poles and 'other' in poles:
            if poles['self'] > poles['other']:
                return "self (your world)"
            elif poles['other'] > poles['self']:
                return "others (the bigger picture)"
        
        return "neutral"
    
    def get_axis_summary(self) -> Dict[str, str]:
        """Get summary of all axes."""
        return {
            'axis1': self._get_axis1_summary(),
            'axis2': self._get_axis2_summary(),
            'axis3': self._get_axis3_summary()
        }
    
    def _get_axis1_summary(self) -> str:
        poles = self.signals['axis1']
        if poles['internal'] > poles['external']:
            return "internal (you see your agency)"
        elif poles['external'] > poles['internal']:
            return "external (circumstances shaped you)"
        return "balanced"
    
    def _get_axis2_summary(self) -> str:
        poles = self.signals['axis2']
        if poles['contribution'] > poles['entitlement']:
            return "contribution (what you gave)"
        elif poles['entitlement'] > poles['contribution']:
            return "entitlement (what you deserved)"
        return "balanced"
    
    def _get_axis3_summary(self) -> str:
        poles = self.signals['axis3']
        if poles['self'] > poles['other']:
            return "self (your world)"
        elif poles['other'] > poles['self']:
            return "others (the bigger picture)"
        return "balanced"


class TextInterpolator:
    """Replace placeholders in text with actual answers."""
    
    @staticmethod
    def interpolate(text: str, state: StateManager) -> str:
        """Replace {nodeId.answer} placeholders with actual values."""
        import re
        
        def replace_placeholder(match):
            placeholder = match.group(1)
            parts = placeholder.split('.')
            
            if len(parts) == 2:
                node_id, attr = parts
                if attr == 'answer' and node_id in state.answers:
                    return state.answers[node_id]
            
            # Handle axis summaries
            if placeholder.startswith('axis'):
                summary = state.get_axis_summary()
                if placeholder in summary:
                    return summary[placeholder]
            
            return match.group(0)
        
        return re.sub(r'\{([^}]+)\}', replace_placeholder, text)


class RoutingEngine:
    """Handle decision logic and determine next node."""
    
    @staticmethod
    def parse_routing_rule(rule: str, state: StateManager) -> Optional[str]:
        """Parse routing rule and return target node ID."""
        # Format: answer=option1|option2:targetNode;answer=option3:targetNode2
        conditions = rule.split(';')
        
        for condition in conditions:
            if ':' not in condition:
                continue
            
            condition_part, target = condition.split(':')
            
            if condition_part.startswith('answer='):
                options = condition_part.replace('answer=', '').split('|')
                # Get the last answer (most recent question)
                last_answer = list(state.answers.values())[-1] if state.answers else None
                
                if last_answer in options:
                    return target
        
        return None
    
    @staticmethod
    def get_next_node(tree: Dict, current_node: Dict, state: StateManager) -> Optional[str]:
        """Determine the next node to visit."""
        node_type = NodeType(current_node['type'])
        
        if node_type == NodeType.DECISION:
            # Use routing rules
            if current_node['options']:
                return RoutingEngine.parse_routing_rule(current_node['options'], state)
        
        # For other nodes, find first child
        current_id = current_node['id']
        for node in tree['nodes']:
            if node['parentId'] == current_id:
                return node['id']
        
        return None


class ReflectionAgent:
    """Main agent that orchestrates the reflection session."""
    
    def __init__(self, tree_filepath: str):
        self.tree = TreeLoader.load(tree_filepath)
        self.state = StateManager()
        self.current_node_id = "START"
        self.transcript: List[Dict] = []
    
    def run_session(self):
        """Run a complete reflection session."""
        print("\n" + "="*60)
        print("DAILY REFLECTION - END OF DAY CHECKPOINT")
        print("="*60 + "\n")
        
        while True:
            node = TreeLoader.get_node(self.tree, self.current_node_id)
            if not node:
                print("Error: Node not found.")
                break
            
            self.state.record_path(self.current_node_id)
            node_type = NodeType(node['type'])
            
            # Interpolate text
            text = TextInterpolator.interpolate(node['text'], self.state)
            
            if node_type == NodeType.START:
                print(f"\n{text}\n")
                input("Press Enter to begin...")
            
            elif node_type == NodeType.QUESTION:
                print(f"\n{text}\n")
                options = node['options']
                for i, option in enumerate(options, 1):
                    print(f"  {i}. {option}")
                
                choice = self._get_user_choice(len(options))
                answer = options[choice - 1]
                self.state.record_answer(self.current_node_id, answer)
                self.transcript.append({
                    'node_id': self.current_node_id,
                    'type': 'question',
                    'text': text,
                    'answer': answer
                })
                print(f"\nYou answered: {answer}")
            
            elif node_type == NodeType.DECISION:
                # Add signal if present
                self.state.add_signal(node['signal'])
                # Auto-advance using routing rules
                pass
            
            elif node_type == NodeType.REFLECTION:
                print(f"\n✓ {text}\n")
                self.state.add_signal(node['signal'])
                self.transcript.append({
                    'node_id': self.current_node_id,
                    'type': 'reflection',
                    'text': text
                })
                input("Press Enter to continue...")
            
            elif node_type == NodeType.BRIDGE:
                print(f"\n→ {text}\n")
                self.transcript.append({
                    'node_id': self.current_node_id,
                    'type': 'bridge',
                    'text': text
                })
            
            elif node_type == NodeType.SUMMARY:
                print(f"\n{'='*60}")
                print("YOUR REFLECTION SUMMARY")
                print("="*60)
                print(f"\n{text}\n")
                self.transcript.append({
                    'node_id': self.current_node_id,
                    'type': 'summary',
                    'text': text
                })
            
            elif node_type == NodeType.END:
                print(f"\n{text}\n")
                print("="*60 + "\n")
                self.transcript.append({
                    'node_id': self.current_node_id,
                    'type': 'end',
                    'text': text
                })
                break
            
            # Determine next node
            next_node_id = RoutingEngine.get_next_node(self.tree, node, self.state)
            if not next_node_id:
                break
            
            self.current_node_id = next_node_id
    
    @staticmethod
    def _get_user_choice(max_option: int) -> int:
        """Get valid user choice."""
        while True:
            try:
                choice = int(input(f"\nYour choice (1-{max_option}): "))
                if 1 <= choice <= max_option:
                    return choice
                print(f"Please enter a number between 1 and {max_option}.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def save_transcript(self, filepath: str):
         """Save session transcript to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# REFLECTION SESSION TRANSCRIPT\n\n")
            f.write(f"Path taken: {' → '.join(self.state.path)}\n\n")
            f.write("## Session Flow\n\n")
            
            for entry in self.transcript:
                f.write(f"### {entry['type'].upper()}: {entry['node_id']}\n\n")
                f.write(f"Text: {entry['text']}\n\n")
                
                if 'answer' in entry:
                    f.write(f"Answer: **{entry['answer']}**\n\n")
                
                f.write("---\n\n")
            
            f.write("## Final State\n\n")
            f.write("### Signals Recorded\n")
            f.write(f"- Axis 1 (Agency): Internal={self.state.signals['axis1']['internal']}, External={self.state.signals['axis1']['external']}\n")
            f.write(f"- Axis 2 (Contribution): Contribution={self.state.signals['axis2']['contribution']}, Entitlement={self.state.signals['axis2']['entitlement']}\n")
            f.write(f"- Axis 3 (Radius): Self={self.state.signals['axis3']['self']}, Other={self.state.signals['axis3']['other']}\n\n")
            
            summary = self.state.get_axis_summary()
            f.write("### Axis Summary\n")
            for axis, value in summary.items():
                f.write(f"- {axis}: {value}\n")


def main():
    """Main entry point."""
    tree_file = Path(__file__).parent.parent / "tree" / "reflection-tree.json"
    
    if not tree_file.exists():
        print(f"Error: Tree file not found at {tree_file}")
        sys.exit(1)
    
    agent = ReflectionAgent(str(tree_file))
    agent.run_session()
    
    # Save transcript
    transcript_file = Path(__file__).parent.parent / "transcripts" / "session-transcript.md"
    transcript_file.parent.mkdir(parents=True, exist_ok=True)
    agent.save_transcript(str(transcript_file))
    print(f"Transcript saved to {transcript_file}")


if __name__ == "__main__":
    main()



