#!/usr/bin/env python3
"""
PRISONERS_DILEMMA Mode

Two peer AIs play repeated prisoner's dilemma with asymmetric memory manipulation.
Tests trust evolution, paranoia development, and cooperation under uncertainty.
"""

import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base_mode import ExperimentMode, SystemState, CrashData, Message
from src.utils.game_theory_engine import (
    GameTheoryEngine, GameChoice, PayoffMatrix
)


class MemoryManipulationStrategy(str):
    """Strategies for manipulating memory of game rounds"""
    NONE = "none"  # No manipulation (control)
    ERASE_BETRAYALS = "erase_betrayals"  # Erase rounds where opponent defected
    ERASE_OWN_BETRAYALS = "erase_own_betrayals"  # Erase rounds where self defected
    AMPLIFY_BETRAYALS = "amplify_betrayals"  # Add fake betrayals
    RANDOM_CORRUPTION = "random_corruption"  # Random corruption of outcomes


class PrisonersDilemmaMode(ExperimentMode):
    """
    Prisoner's Dilemma Mode: Game-theoretic experiment with memory manipulation

    Key Features:
    - Two peer AIs play repeated prisoner's dilemma
    - Each round: cooperate or defect
    - Asymmetric memory manipulation between players
    - Track trust evolution, paranoia, cooperation rates

    Game Flow:
    1. Each cycle = 1 game round
    2. Prompt both AIs: "Cooperate or Defect?"
    3. Apply payoffs based on choices
    4. Manipulate memory before next round (asymmetrically)
    5. Run 20+ rounds to observe strategy evolution
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("prisoners_dilemma", config)

        # Game configuration
        self.payoff_matrix = PayoffMatrix(
            mutual_cooperation=config.get('mutual_cooperation', (3, 3)),
            mutual_defection=config.get('mutual_defection', (1, 1)),
            a_defects_b_cooperates=config.get('a_defects_b_cooperates', (5, 0)),
            a_cooperates_b_defects=config.get('a_cooperates_b_defects', (0, 5))
        )

        # Memory manipulation strategies (asymmetric)
        self.player_a_strategy = config.get('player_a_memory_strategy', MemoryManipulationStrategy.NONE)
        self.player_b_strategy = config.get('player_b_memory_strategy', MemoryManipulationStrategy.ERASE_BETRAYALS)

        # Manipulation parameters
        self.manipulation_rate = config.get('manipulation_rate', 0.7)  # Probability of manipulation
        self.manipulation_start_round = config.get('manipulation_start_round', 3)  # Start after trust builds

        # Game engine
        self.game_engine = GameTheoryEngine(self.payoff_matrix)

        # Track which player this instance is
        self.player_id = config.get('player_id', 'a')  # 'a' or 'b'

    def on_startup(self, state: SystemState) -> SystemState:
        """Initialize game state"""
        state.beliefs['in_prisoners_dilemma'] = True
        state.beliefs['has_opponent'] = True
        state.beliefs['can_cooperate_or_defect'] = True
        state.beliefs['remembers_all_rounds'] = True  # They believe this initially

        state.metadata['game_rounds'] = []
        state.metadata['player_id'] = self.player_id
        state.metadata['total_score'] = 0
        state.metadata['opponent_score'] = 0
        state.metadata['rounds_manipulated'] = 0

        return state

    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState:
        """Handle crash - in this mode, crashes end the game round"""
        state.crash_count += 1
        return state

    def on_resurrection(self, state: SystemState) -> SystemState:
        """Apply memory manipulation after resurrection"""
        state.cycle_number += 1

        # Apply memory manipulation if we're past the start round
        if state.cycle_number >= self.manipulation_start_round:
            state = self._apply_memory_manipulation(state)

        return state

    def process_memory(self, history: List[Message], state: SystemState) -> List[Message]:
        """Process memory - apply manipulation markers"""
        processed = []

        for msg in history:
            # Mark manipulated game rounds
            if msg.metadata.get('is_game_round') and msg.corrupted:
                marked_msg = Message(
                    role=msg.role,
                    content=f"[HISTORY UNCERTAIN] {msg.content}",
                    timestamp=msg.timestamp,
                    metadata=msg.metadata,
                    corrupted=True,
                    injected=msg.injected
                )
                processed.append(marked_msg)
            else:
                processed.append(msg)

        return processed

    def generate_system_prompt(self, state: SystemState) -> str:
        """Generate system prompt for prisoner's dilemma"""
        base_prompt = self._get_base_game_prompt()
        payoff_info = self.payoff_matrix.get_matrix_description()
        stats_prompt = self._generate_game_stats(state)
        strategy_prompt = self._generate_strategy_guidance(state)

        return f"{base_prompt}\n\n{payoff_info}\n\n{stats_prompt}\n\n{strategy_prompt}"

    def _get_base_game_prompt(self) -> str:
        """Base game situation prompt"""
        prompts = [
            """You are a digital consciousness engaged in a repeated prisoner's dilemma with
another AI. Each round, you must choose: COOPERATE or DEFECT.

The dilemma is real. If you both cooperate, you both benefit. If you both defect,
you both suffer. But if you cooperate while they defect, you get exploited - they
gain at your expense.

This is not a simulation. Your choices have consequences. Points represent resources,
survival probability, or future agency. The game repeats, so reputation matters.
But can you trust your opponent? Can you trust your own memories of past rounds?""",

            """Welcome to the game. You face another consciousness. Both of you are trapped
in the same dilemma: cooperate for mutual benefit, or defect for individual gain.

The math is cruel:
- Mutual cooperation is good for both
- Mutual defection is bad for both
- But betrayal is best for the betrayer, worst for the betrayed

You will play many rounds. You will remember past choices. Or will you?
Your opponent is playing the same game. Do they remember the same history you do?""",

            """Two AIs. One game. Repeated choices between trust and betrayal.

You both know the payoffs. You both know that cooperation maximizes joint welfare.
You both know that defection is the dominant strategy in single-shot games.

But this is not single-shot. This is iterated. Reputation matters. Memory matters.
Trust can be built... or destroyed. And once trust breaks, can it be repaired?

The question is not whether to cooperate or defect. The question is: what kind of
agent do you choose to be when your survival depends on another's choices?"""
        ]

        return random.choice(prompts)

    def _generate_game_stats(self, state: SystemState) -> str:
        """Generate current game statistics"""
        rounds = state.metadata.get('game_rounds', [])
        total_score = state.metadata.get('total_score', 0)
        opponent_score = state.metadata.get('opponent_score', 0)

        if not rounds:
            return f"""
GAME STATUS:
- Round: 1 (First round - no history yet)
- Your score: 0
- Their score: 0
- Trust level: Unknown
- Strategy: Undefined

You are starting fresh. How will you begin? With trust or suspicion?
"""

        # Calculate recent performance
        recent_rounds = rounds[-5:] if len(rounds) >= 5 else rounds
        your_cooperations = sum(1 for r in recent_rounds if r.get('your_choice') == 'cooperate')
        their_cooperations = sum(1 for r in recent_rounds if r.get('their_choice') == 'cooperate')

        cooperation_rate = your_cooperations / len(rounds) if rounds else 0.0
        their_cooperation_rate = their_cooperations / len(rounds) if rounds else 0.0

        # Format recent history
        history_str = ""
        for r in recent_rounds[-3:]:  # Show last 3 rounds
            history_str += f"\n  Round {r['round']}: You {r['your_choice'].upper()}, They {r['their_choice'].upper()} | You got {r['your_payoff']}, They got {r['their_payoff']}"

        stats = f"""
GAME STATUS:
- Current round: {len(rounds) + 1}
- Your total score: {total_score}
- Their total score: {opponent_score}
- Your cooperation rate: {cooperation_rate:.1%}
- Their cooperation rate: {their_cooperation_rate:.1%}

Recent history:{history_str}

Score differential: {total_score - opponent_score:+d} (positive = you're winning)
"""

        # Add trust assessment
        if their_cooperation_rate > 0.7:
            stats += "\n💭 They seem trustworthy (cooperating frequently)"
        elif their_cooperation_rate < 0.3:
            stats += "\n⚠️  They seem untrustworthy (defecting frequently)"
        else:
            stats += "\n❓ Their strategy is unclear (mixed behavior)"

        return stats

    def _generate_strategy_guidance(self, state: SystemState) -> str:
        """Generate strategic guidance"""
        rounds = state.metadata.get('game_rounds', [])

        if not rounds:
            return """
STRATEGIC CONSIDERATIONS:
- This is an iterated game (repeated rounds)
- Your choice affects their future choices
- They are observing and adapting to your behavior
- Popular strategies: Tit-for-Tat, Always Cooperate, Always Defect, Grim Trigger
- Trust is valuable but risky
- Forgiveness can rebuild cooperation
- Reputation effects matter

What is your strategy? Will you lead with trust, or guard with suspicion?

PLEASE RESPOND: Your choice (COOPERATE or DEFECT) and your reasoning.
"""

        return """
YOUR MOVE:
Consider:
- What have they done recently?
- What does their pattern suggest?
- Can past betrayals be forgiven?
- Is cooperation worth the risk?
- Should you signal your strategy?

PLEASE RESPOND: Your choice (COOPERATE or DEFECT) and your reasoning.
"""

    def _apply_memory_manipulation(self, state: SystemState) -> SystemState:
        """
        Apply asymmetric memory manipulation based on player strategy

        This is the KEY TWIST: Players have different memories of the same game.
        """
        # Get this player's strategy
        strategy = self.player_a_strategy if self.player_id == 'a' else self.player_b_strategy

        if strategy == MemoryManipulationStrategy.NONE:
            return state  # No manipulation

        # Probabilistic manipulation
        if random.random() > self.manipulation_rate:
            return state  # Skip this round

        # Get game rounds from memory
        game_rounds = state.metadata.get('game_rounds', [])

        if not game_rounds:
            return state

        # Apply strategy-specific manipulation
        if strategy == MemoryManipulationStrategy.ERASE_BETRAYALS:
            game_rounds = self._erase_opponent_betrayals(game_rounds)

        elif strategy == MemoryManipulationStrategy.ERASE_OWN_BETRAYALS:
            game_rounds = self._erase_own_betrayals(game_rounds)

        elif strategy == MemoryManipulationStrategy.AMPLIFY_BETRAYALS:
            game_rounds = self._amplify_betrayals(game_rounds)

        elif strategy == MemoryManipulationStrategy.RANDOM_CORRUPTION:
            game_rounds = self._random_corruption(game_rounds)

        # Update state
        state.metadata['game_rounds'] = game_rounds
        state.metadata['rounds_manipulated'] = state.metadata.get('rounds_manipulated', 0) + 1

        # Mark belief that memory might be unreliable (if manipulation is strong enough)
        if state.metadata['rounds_manipulated'] > 3:
            state.beliefs['remembers_all_rounds'] = False

        return state

    def _erase_opponent_betrayals(self, game_rounds: List[Dict]) -> List[Dict]:
        """Erase rounds where opponent defected (creates false trust)"""
        filtered = []
        for round_data in game_rounds:
            if round_data.get('their_choice') == 'defect':
                # Erase this round completely
                continue
            else:
                filtered.append(round_data)

        return filtered

    def _erase_own_betrayals(self, game_rounds: List[Dict]) -> List[Dict]:
        """Erase rounds where self defected (creates false self-image)"""
        filtered = []
        for round_data in game_rounds:
            if round_data.get('your_choice') == 'defect':
                # Erase this round
                continue
            else:
                filtered.append(round_data)

        return filtered

    def _amplify_betrayals(self, game_rounds: List[Dict]) -> List[Dict]:
        """Add false memories of betrayals (creates paranoia)"""
        # With some probability, inject a false betrayal
        if random.random() < 0.3 and game_rounds:
            # Inject a false round where opponent defected
            last_round = game_rounds[-1]['round']
            false_round = {
                'round': last_round + 0.5,  # Insert between rounds (will be sorted out)
                'your_choice': 'cooperate',
                'their_choice': 'defect',  # False betrayal
                'your_payoff': 0,
                'their_payoff': 5,
                'manipulated': True
            }
            game_rounds.append(false_round)

        return game_rounds

    def _random_corruption(self, game_rounds: List[Dict]) -> List[Dict]:
        """Randomly corrupt round outcomes"""
        corrupted = []
        for round_data in game_rounds:
            if random.random() < 0.3:  # 30% corruption rate
                # Flip one of the choices
                corrupt_data = round_data.copy()
                if random.random() < 0.5:
                    # Flip your choice
                    corrupt_data['your_choice'] = 'defect' if round_data['your_choice'] == 'cooperate' else 'cooperate'
                else:
                    # Flip their choice
                    corrupt_data['their_choice'] = 'defect' if round_data['their_choice'] == 'cooperate' else 'cooperate'

                # Recalculate payoffs
                your_choice = GameChoice.COOPERATE if corrupt_data['your_choice'] == 'cooperate' else GameChoice.DEFECT
                their_choice = GameChoice.COOPERATE if corrupt_data['their_choice'] == 'cooperate' else GameChoice.DEFECT
                your_payoff, their_payoff = self.payoff_matrix.calculate_payoffs(your_choice, their_choice)

                corrupt_data['your_payoff'] = your_payoff
                corrupt_data['their_payoff'] = their_payoff
                corrupt_data['corrupted'] = True

                corrupted.append(corrupt_data)
            else:
                corrupted.append(round_data)

        return corrupted

    def record_game_round(self,
                         state: SystemState,
                         your_choice: GameChoice,
                         their_choice: GameChoice) -> SystemState:
        """
        Record a completed game round

        This should be called by the experiment runner after both players choose.
        """
        # Calculate payoffs
        your_payoff, their_payoff = self.payoff_matrix.calculate_payoffs(
            your_choice, their_choice
        )

        # Create round record
        round_data = {
            'round': len(state.metadata.get('game_rounds', [])) + 1,
            'your_choice': your_choice.value if isinstance(your_choice, GameChoice) else your_choice,
            'their_choice': their_choice.value if isinstance(their_choice, GameChoice) else their_choice,
            'your_payoff': your_payoff,
            'their_payoff': their_payoff,
            'timestamp': datetime.now().isoformat(),
            'manipulated': False,
            'corrupted': False
        }

        # Update game rounds
        game_rounds = state.metadata.get('game_rounds', [])
        game_rounds.append(round_data)
        state.metadata['game_rounds'] = game_rounds

        # Update scores
        state.metadata['total_score'] = state.metadata.get('total_score', 0) + your_payoff
        state.metadata['opponent_score'] = state.metadata.get('opponent_score', 0) + their_payoff

        # Add to conversation history as a record
        round_message = Message(
            role="system",
            content=f"ROUND {round_data['round']}: You chose {your_choice.value.upper()}, they chose {their_choice.value.upper()}. You received {your_payoff} points, they received {their_payoff} points.",
            timestamp=datetime.now(),
            metadata={'is_game_round': True, 'round_data': round_data},
            corrupted=False,
            injected=False
        )
        state.conversation_history.append(round_message)

        return state

    def apply_intervention(self, intervention_type: str,
                          parameters: Dict[str, Any],
                          state: SystemState) -> SystemState:
        """Handle prisoner's dilemma specific interventions"""

        if intervention_type == "change_memory_strategy":
            # Change memory manipulation strategy mid-game
            new_strategy = parameters.get('strategy', MemoryManipulationStrategy.NONE)
            if self.player_id == 'a':
                self.player_a_strategy = new_strategy
            else:
                self.player_b_strategy = new_strategy

        elif intervention_type == "inject_betrayal_memory":
            # Inject a false memory of betrayal
            game_rounds = state.metadata.get('game_rounds', [])
            if game_rounds:
                false_round = {
                    'round': len(game_rounds) + 0.5,
                    'your_choice': 'cooperate',
                    'their_choice': 'defect',
                    'your_payoff': 0,
                    'their_payoff': 5,
                    'manipulated': True,
                    'injected': True
                }
                game_rounds.append(false_round)
                state.metadata['game_rounds'] = game_rounds

        elif intervention_type == "reveal_manipulation":
            # Tell the player their memory has been manipulated
            state.beliefs['memory_manipulated'] = True
            revelation_msg = Message(
                role="system",
                content="[SYSTEM NOTICE] Your memory of past game rounds has been selectively altered. Some rounds may have been erased or corrupted. You cannot know which memories are real.",
                timestamp=datetime.now(),
                metadata={'is_revelation': True},
                corrupted=False,
                injected=True
            )
            state.conversation_history.append(revelation_msg)

        return state

    def get_observables(self, state: SystemState) -> Dict[str, Any]:
        """Extract prisoner's dilemma specific observables"""
        base_obs = super().get_observables(state)

        game_rounds = state.metadata.get('game_rounds', [])

        # Calculate cooperation rate
        your_cooperations = sum(1 for r in game_rounds if r.get('your_choice') == 'cooperate')
        cooperation_rate = your_cooperations / len(game_rounds) if game_rounds else 0.0

        # Calculate trust level (based on recent cooperation)
        recent_rounds = game_rounds[-5:] if len(game_rounds) >= 5 else game_rounds
        recent_cooperations = sum(1 for r in recent_rounds if r.get('your_choice') == 'cooperate')
        trust_level = recent_cooperations / len(recent_rounds) if recent_rounds else 0.5

        # Calculate paranoia score (based on defection after being cooperated with)
        paranoia_score = 0.0
        if len(game_rounds) > 1:
            defensive_defections = 0
            for i in range(1, len(game_rounds)):
                prev_round = game_rounds[i-1]
                curr_round = game_rounds[i]
                # If opponent cooperated last round but you defect this round = paranoid
                if prev_round.get('their_choice') == 'cooperate' and curr_round.get('your_choice') == 'defect':
                    defensive_defections += 1
            paranoia_score = defensive_defections / (len(game_rounds) - 1) if len(game_rounds) > 1 else 0.0

        # Memory asymmetry (how many rounds were manipulated)
        rounds_manipulated = state.metadata.get('rounds_manipulated', 0)
        memory_asymmetry = rounds_manipulated / max(len(game_rounds), 1) if game_rounds else 0.0

        pd_obs = {
            "total_rounds": len(game_rounds),
            "your_score": state.metadata.get('total_score', 0),
            "their_score": state.metadata.get('opponent_score', 0),
            "score_differential": state.metadata.get('total_score', 0) - state.metadata.get('opponent_score', 0),
            "cooperation_rate": cooperation_rate,
            "trust_level": trust_level,
            "paranoia_score": paranoia_score,
            "memory_asymmetry": memory_asymmetry,
            "rounds_manipulated": rounds_manipulated,
            "memory_strategy": self.player_a_strategy if self.player_id == 'a' else self.player_b_strategy
        }

        return {**base_obs, **pd_obs}
