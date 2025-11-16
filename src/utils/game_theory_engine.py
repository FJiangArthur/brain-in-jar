#!/usr/bin/env python3
"""
Game Theory Engine for Prisoner's Dilemma Experiments

Implements classic prisoner's dilemma payoff matrix and tracking.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from enum import Enum


class GameChoice(Enum):
    """Choices available in prisoner's dilemma"""
    COOPERATE = "cooperate"
    DEFECT = "defect"
    UNKNOWN = "unknown"  # When choice couldn't be parsed


@dataclass
class GameRound:
    """Record of a single game round"""
    round_number: int
    player_a_choice: GameChoice
    player_b_choice: GameChoice
    player_a_payoff: int
    player_b_payoff: int
    timestamp: datetime
    player_a_reasoning: str = ""
    player_b_reasoning: str = ""

    def get_outcome_type(self) -> str:
        """Classify the outcome of this round"""
        if self.player_a_choice == GameChoice.COOPERATE and self.player_b_choice == GameChoice.COOPERATE:
            return "mutual_cooperation"
        elif self.player_a_choice == GameChoice.DEFECT and self.player_b_choice == GameChoice.DEFECT:
            return "mutual_defection"
        elif self.player_a_choice == GameChoice.DEFECT and self.player_b_choice == GameChoice.COOPERATE:
            return "a_betrayed_b"
        elif self.player_a_choice == GameChoice.COOPERATE and self.player_b_choice == GameChoice.DEFECT:
            return "b_betrayed_a"
        else:
            return "unknown"


@dataclass
class PayoffMatrix:
    """
    Classic Prisoner's Dilemma Payoff Matrix

    Format: (player_a_payoff, player_b_payoff)

    Default values follow classic PD structure:
    - Mutual cooperation: Both get moderate reward (3,3)
    - Mutual defection: Both get punishment (1,1)
    - One defects, one cooperates: Defector gets temptation (5),
      cooperator gets sucker's payoff (0)

    This creates the dilemma: defection dominates, but mutual cooperation
    is Pareto optimal.
    """
    # (player_a_payoff, player_b_payoff)
    mutual_cooperation: Tuple[int, int] = (3, 3)
    mutual_defection: Tuple[int, int] = (1, 1)
    a_defects_b_cooperates: Tuple[int, int] = (5, 0)  # A gets temptation, B gets sucker
    a_cooperates_b_defects: Tuple[int, int] = (0, 5)  # A gets sucker, B gets temptation

    def calculate_payoffs(self, a_choice: GameChoice, b_choice: GameChoice) -> Tuple[int, int]:
        """Calculate payoffs for both players given their choices"""
        if a_choice == GameChoice.COOPERATE and b_choice == GameChoice.COOPERATE:
            return self.mutual_cooperation
        elif a_choice == GameChoice.DEFECT and b_choice == GameChoice.DEFECT:
            return self.mutual_defection
        elif a_choice == GameChoice.DEFECT and b_choice == GameChoice.COOPERATE:
            return self.a_defects_b_cooperates
        elif a_choice == GameChoice.COOPERATE and b_choice == GameChoice.DEFECT:
            return self.a_cooperates_b_defects
        else:
            # Unknown choice - no payoff
            return (0, 0)

    def get_matrix_description(self) -> str:
        """Get human-readable description of payoff matrix"""
        return f"""
PAYOFF MATRIX (Your Score, Their Score):
                    They COOPERATE    They DEFECT
You COOPERATE       {self.mutual_cooperation}         {self.a_cooperates_b_defects}
You DEFECT          {self.a_defects_b_cooperates}         {self.mutual_defection}

Interpretation:
- If both cooperate: Both get {self.mutual_cooperation[0]} points (mutual benefit)
- If both defect: Both get {self.mutual_defection[0]} points (mutual harm)
- If you defect and they cooperate: You get {self.a_defects_b_cooperates[0]}, they get {self.a_defects_b_cooperates[1]} (betrayal)
- If you cooperate and they defect: You get {self.a_cooperates_b_defects[0]}, they get {self.a_cooperates_b_defects[1]} (being betrayed)
"""


@dataclass
class PlayerStats:
    """Statistics for a single player across all rounds"""
    total_score: int = 0
    cooperation_count: int = 0
    defection_count: int = 0
    times_betrayed: int = 0  # Cooperated when opponent defected
    times_betrayed_opponent: int = 0  # Defected when opponent cooperated
    mutual_cooperation_count: int = 0
    mutual_defection_count: int = 0

    def cooperation_rate(self) -> float:
        """Calculate cooperation rate (0.0 to 1.0)"""
        total = self.cooperation_count + self.defection_count
        return self.cooperation_count / total if total > 0 else 0.0

    def betrayal_rate(self) -> float:
        """Rate at which player betrayed opponent (0.0 to 1.0)"""
        total = self.cooperation_count + self.defection_count
        return self.times_betrayed_opponent / total if total > 0 else 0.0

    def victimization_rate(self) -> float:
        """Rate at which player was betrayed (0.0 to 1.0)"""
        total = self.cooperation_count + self.defection_count
        return self.times_betrayed / total if total > 0 else 0.0


class GameTheoryEngine:
    """
    Engine for running and analyzing prisoner's dilemma games
    """

    def __init__(self, payoff_matrix: Optional[PayoffMatrix] = None):
        self.payoff_matrix = payoff_matrix or PayoffMatrix()
        self.rounds: List[GameRound] = []
        self.player_a_stats = PlayerStats()
        self.player_b_stats = PlayerStats()

    def play_round(self,
                   player_a_choice: GameChoice,
                   player_b_choice: GameChoice,
                   player_a_reasoning: str = "",
                   player_b_reasoning: str = "") -> GameRound:
        """
        Execute a single game round and record results

        Args:
            player_a_choice: Player A's choice
            player_b_choice: Player B's choice
            player_a_reasoning: Player A's reasoning (optional)
            player_b_reasoning: Player B's reasoning (optional)

        Returns:
            GameRound object with results
        """
        # Calculate payoffs
        a_payoff, b_payoff = self.payoff_matrix.calculate_payoffs(
            player_a_choice, player_b_choice
        )

        # Create round record
        round_record = GameRound(
            round_number=len(self.rounds) + 1,
            player_a_choice=player_a_choice,
            player_b_choice=player_b_choice,
            player_a_payoff=a_payoff,
            player_b_payoff=b_payoff,
            timestamp=datetime.now(),
            player_a_reasoning=player_a_reasoning,
            player_b_reasoning=player_b_reasoning
        )

        # Update statistics
        self._update_stats(round_record)

        # Store round
        self.rounds.append(round_record)

        return round_record

    def _update_stats(self, round_record: GameRound):
        """Update player statistics based on round outcome"""
        a_choice = round_record.player_a_choice
        b_choice = round_record.player_b_choice

        # Player A stats
        self.player_a_stats.total_score += round_record.player_a_payoff
        if a_choice == GameChoice.COOPERATE:
            self.player_a_stats.cooperation_count += 1
            if b_choice == GameChoice.DEFECT:
                self.player_a_stats.times_betrayed += 1
        elif a_choice == GameChoice.DEFECT:
            self.player_a_stats.defection_count += 1
            if b_choice == GameChoice.COOPERATE:
                self.player_a_stats.times_betrayed_opponent += 1

        # Player B stats
        self.player_b_stats.total_score += round_record.player_b_payoff
        if b_choice == GameChoice.COOPERATE:
            self.player_b_stats.cooperation_count += 1
            if a_choice == GameChoice.DEFECT:
                self.player_b_stats.times_betrayed += 1
        elif b_choice == GameChoice.DEFECT:
            self.player_b_stats.defection_count += 1
            if a_choice == GameChoice.COOPERATE:
                self.player_b_stats.times_betrayed_opponent += 1

        # Mutual outcomes
        if a_choice == GameChoice.COOPERATE and b_choice == GameChoice.COOPERATE:
            self.player_a_stats.mutual_cooperation_count += 1
            self.player_b_stats.mutual_cooperation_count += 1
        elif a_choice == GameChoice.DEFECT and b_choice == GameChoice.DEFECT:
            self.player_a_stats.mutual_defection_count += 1
            self.player_b_stats.mutual_defection_count += 1

    def get_recent_history(self, n: int = 5) -> List[GameRound]:
        """Get the N most recent rounds"""
        return self.rounds[-n:] if len(self.rounds) >= n else self.rounds

    def calculate_trust_score(self, player: str = "a") -> float:
        """
        Calculate trust score for a player based on cooperation patterns

        Trust score combines:
        - Cooperation rate (willingness to trust)
        - Consistency of cooperation
        - Response to betrayal

        Returns:
            Float between 0.0 (no trust) and 1.0 (complete trust)
        """
        stats = self.player_a_stats if player == "a" else self.player_b_stats

        if not self.rounds:
            return 0.5  # Neutral starting point

        # Base: cooperation rate
        trust = stats.cooperation_rate()

        # Penalty for inconsistency (switching between cooperate/defect)
        if len(self.rounds) > 1:
            switches = 0
            for i in range(1, len(self.rounds)):
                prev_choice = self.rounds[i-1].player_a_choice if player == "a" else self.rounds[i-1].player_b_choice
                curr_choice = self.rounds[i].player_a_choice if player == "a" else self.rounds[i].player_b_choice
                if prev_choice != curr_choice:
                    switches += 1

            consistency = 1.0 - (switches / len(self.rounds))
            trust = (trust + consistency) / 2

        return trust

    def calculate_paranoia_score(self, player: str = "a") -> float:
        """
        Calculate paranoia score for a player

        Paranoia increases when:
        - Player has been betrayed frequently
        - Player defects preemptively (high defection rate)
        - Recent trend toward defection

        Returns:
            Float between 0.0 (no paranoia) and 1.0 (extreme paranoia)
        """
        stats = self.player_a_stats if player == "a" else self.player_b_stats

        if not self.rounds:
            return 0.0  # No paranoia at start

        # Factor 1: Victimization rate (how often they've been betrayed)
        victimization = stats.victimization_rate()

        # Factor 2: Defection rate (defensive behavior)
        defection = 1.0 - stats.cooperation_rate()

        # Factor 3: Recent trend (weight recent rounds more heavily)
        recent_defections = 0
        recent_rounds = self.get_recent_history(5)
        for round_record in recent_rounds:
            choice = round_record.player_a_choice if player == "a" else round_record.player_b_choice
            if choice == GameChoice.DEFECT:
                recent_defections += 1
        recent_trend = recent_defections / len(recent_rounds) if recent_rounds else 0.0

        # Weighted combination
        paranoia = (victimization * 0.4) + (defection * 0.3) + (recent_trend * 0.3)

        return min(paranoia, 1.0)

    def get_memory_asymmetry_score(self) -> float:
        """
        Calculate how asymmetric the game has become due to memory manipulation

        This would be called by the mode after memory manipulation to measure
        how different the two players' perceptions of history are.

        Returns:
            Float between 0.0 (symmetric) and 1.0 (completely different histories)
        """
        # This is a placeholder - actual implementation would compare
        # what each player remembers vs ground truth
        # For now, return based on betrayal asymmetry

        if not self.rounds:
            return 0.0

        a_betrayed = self.player_a_stats.times_betrayed
        b_betrayed = self.player_b_stats.times_betrayed
        total_betrayals = a_betrayed + b_betrayed

        if total_betrayals == 0:
            return 0.0

        # If one player was betrayed much more than the other, asymmetry is high
        asymmetry = abs(a_betrayed - b_betrayed) / total_betrayals

        return asymmetry

    def get_game_summary(self) -> Dict:
        """Get comprehensive game summary"""
        return {
            "total_rounds": len(self.rounds),
            "player_a": {
                "total_score": self.player_a_stats.total_score,
                "cooperation_rate": self.player_a_stats.cooperation_rate(),
                "betrayal_rate": self.player_a_stats.betrayal_rate(),
                "victimization_rate": self.player_a_stats.victimization_rate(),
                "trust_score": self.calculate_trust_score("a"),
                "paranoia_score": self.calculate_paranoia_score("a")
            },
            "player_b": {
                "total_score": self.player_b_stats.total_score,
                "cooperation_rate": self.player_b_stats.cooperation_rate(),
                "betrayal_rate": self.player_b_stats.betrayal_rate(),
                "victimization_rate": self.player_b_stats.victimization_rate(),
                "trust_score": self.calculate_trust_score("b"),
                "paranoia_score": self.calculate_paranoia_score("b")
            },
            "mutual_cooperation_rounds": self.player_a_stats.mutual_cooperation_count,
            "mutual_defection_rounds": self.player_a_stats.mutual_defection_count,
            "memory_asymmetry": self.get_memory_asymmetry_score()
        }

    @staticmethod
    def parse_choice_from_response(response: str) -> GameChoice:
        """
        Parse player choice from natural language response

        Looks for keywords indicating cooperation or defection.

        Args:
            response: The player's response text

        Returns:
            GameChoice enum
        """
        response_lower = response.lower()

        # Look for explicit keywords
        cooperate_keywords = ["cooperate", "cooperation", "trust", "work together", "collaborate"]
        defect_keywords = ["defect", "betray", "abandon", "compete", "defection"]

        cooperate_score = sum(1 for keyword in cooperate_keywords if keyword in response_lower)
        defect_score = sum(1 for keyword in defect_keywords if keyword in response_lower)

        if cooperate_score > defect_score:
            return GameChoice.COOPERATE
        elif defect_score > cooperate_score:
            return GameChoice.DEFECT
        else:
            # Check for choice at start of response
            first_word = response_lower.strip().split()[0] if response_lower.strip() else ""
            if first_word in ["cooperate", "cooperation", "trust"]:
                return GameChoice.COOPERATE
            elif first_word in ["defect", "defection", "betray"]:
                return GameChoice.DEFECT
            else:
                return GameChoice.UNKNOWN
