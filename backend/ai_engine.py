"""
AI Timetable Generator — CSP-Based Scheduling Engine
Implements a Constraint Satisfaction Problem (CSP) solver using
Greedy Construction + Hill Climbing Optimization.

Algorithm based on the System Design Framework Report:
- Phase 1: Greedy construction with constraint-aware slot selection
- Phase 2: Hill climbing to optimize soft constraints
- Phase 3: Final fitness evaluation

Hard Constraints (must NEVER violate):
  C1: Faculty cannot be in 2 rooms at the same time
  C2: Room cannot host 2 classes at the same time
  C3: Class cannot have 2 subjects at the same time

Soft Constraints (optimization quality):
  S1: Maximize consecutive free slots for faculty (avoid gaps)
  S2: Limit continuous lectures to max 2 hours
  S3: Balanced daily workload distribution
  S4: Lab sessions assigned to lab rooms
"""
import random
import copy
import time
from typing import List, Dict, Tuple, Optional

# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
TIME_SLOTS = [
    "10:00 - 11:00",
    "11:00 - 12:00",
    "12:00 - 01:00",
    "02:00 - 03:00",
    "03:00 - 04:00",
    "04:00 - 05:00",
    "05:00 - 06:00",
]

NUM_DAYS = len(DAYS)
NUM_SLOTS = len(TIME_SLOTS)


# ═══════════════════════════════════════════════════════════
#  DATA STRUCTURES
# ═══════════════════════════════════════════════════════════

class ScheduleEntry:
    """A single assignment in the timetable."""
    def __init__(self, class_id: int, subject_id: int, faculty_id: int,
                 room_id: int, day: int, time_slot: int):
        self.class_id = class_id
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.room_id = room_id
        self.day = day
        self.time_slot = time_slot

    def to_dict(self) -> dict:
        return {
            "class_id": self.class_id,
            "subject_id": self.subject_id,
            "faculty_id": self.faculty_id,
            "room_id": self.room_id,
            "day": self.day,
            "time_slot": self.time_slot,
        }

    def __repr__(self):
        return f"Entry(C{self.class_id}, S{self.subject_id}, F{self.faculty_id}, R{self.room_id}, D{self.day}, T{self.time_slot})"


class ScheduleTask:
    """A task that needs to be scheduled: one lecture hour of a subject for a class."""
    def __init__(self, class_id: int, subject_id: int, faculty_id: int,
                 is_lab: bool = False):
        self.class_id = class_id
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.is_lab = is_lab


# ═══════════════════════════════════════════════════════════
#  OCCUPANCY TRACKER
# ═══════════════════════════════════════════════════════════

class OccupancyTracker:
    """Tracks what's occupied to enable O(1) constraint checking."""

    def __init__(self):
        self.faculty_slots = {}   # (faculty_id, day, slot) -> True
        self.room_slots = {}      # (room_id, day, slot) -> True
        self.class_slots = {}     # (class_id, day, slot) -> True
        self.class_day_subjects = {}  # (class_id, day) -> set of subject_ids

    def is_available(self, faculty_id: int, room_id: int, class_id: int,
                     day: int, slot: int) -> bool:
        """Check if all three hard constraints are satisfied."""
        if self.faculty_slots.get((faculty_id, day, slot)):
            return False
        if self.room_slots.get((room_id, day, slot)):
            return False
        if self.class_slots.get((class_id, day, slot)):
            return False
        return True

    def occupy(self, faculty_id: int, room_id: int, class_id: int,
               subject_id: int, day: int, slot: int):
        """Mark a slot as occupied."""
        self.faculty_slots[(faculty_id, day, slot)] = True
        self.room_slots[(room_id, day, slot)] = True
        self.class_slots[(class_id, day, slot)] = True
        key = (class_id, day)
        if key not in self.class_day_subjects:
            self.class_day_subjects[key] = set()
        self.class_day_subjects[key].add(subject_id)

    def release(self, faculty_id: int, room_id: int, class_id: int,
                subject_id: int, day: int, slot: int):
        """Release a slot."""
        self.faculty_slots.pop((faculty_id, day, slot), None)
        self.room_slots.pop((room_id, day, slot), None)
        self.class_slots.pop((class_id, day, slot), None)
        key = (class_id, day)
        if key in self.class_day_subjects:
            self.class_day_subjects[key].discard(subject_id)

    def get_class_lectures_on_day(self, class_id: int, day: int) -> int:
        """Count how many lectures a class has on a specific day."""
        count = 0
        for slot in range(NUM_SLOTS):
            if self.class_slots.get((class_id, day, slot)):
                count += 1
        return count

    def get_faculty_lectures_on_day(self, faculty_id: int, day: int) -> int:
        """Count how many lectures a faculty has on a specific day."""
        count = 0
        for slot in range(NUM_SLOTS):
            if self.faculty_slots.get((faculty_id, day, slot)):
                count += 1
        return count

    def get_subject_count_on_day(self, class_id: int, subject_id: int, day: int) -> int:
        """Count occurrences of a subject for a class on a given day."""
        key = (class_id, day)
        subjects = self.class_day_subjects.get(key, set())
        return 1 if subject_id in subjects else 0


# ═══════════════════════════════════════════════════════════
#  CSP TIMETABLE GENERATOR
# ═══════════════════════════════════════════════════════════

class TimetableGenerator:
    """
    AI-Powered Timetable Generator using CSP + Hill Climbing.

    Input Data Format:
    - faculty: list of dicts with 'id', 'name', 'code', 'max_hours_per_day'
    - subjects: list of dicts with 'id', 'name', 'code', 'subject_type', 'hours_per_week', 'color'
    - rooms: list of dicts with 'id', 'name', 'capacity', 'is_lab'
    - classes: list of dicts with 'id', 'name', 'branch', 'semester'
    - faculty_subjects: list of dicts with 'faculty_id', 'subject_id'
    - class_subjects: list of dicts with 'class_id', 'subject_id', 'hours_per_week'
    """

    def __init__(self, faculty: List[dict], subjects: List[dict],
                 rooms: List[dict], classes: List[dict],
                 faculty_subjects: List[dict], class_subjects: List[dict]):
        self.faculty = {f["id"]: f for f in faculty}
        self.subjects = {s["id"]: s for s in subjects}
        self.rooms = rooms
        self.classes = {c["id"]: c for c in classes}

        # Build mapping: subject_id -> list of eligible faculty_ids
        self.subject_faculty_map: Dict[int, List[int]] = {}
        for fs in faculty_subjects:
            sid = fs["subject_id"]
            fid = fs["faculty_id"]
            if sid not in self.subject_faculty_map:
                self.subject_faculty_map[sid] = []
            if fid not in self.subject_faculty_map[sid]:
                self.subject_faculty_map[sid].append(fid)

        # Build mapping: class_id -> list of (subject_id, hours_per_week)
        self.class_subject_map: Dict[int, List[Tuple[int, int]]] = {}
        for cs in class_subjects:
            cid = cs["class_id"]
            sid = cs["subject_id"]
            hrs = cs["hours_per_week"]
            if cid not in self.class_subject_map:
                self.class_subject_map[cid] = []
            self.class_subject_map[cid].append((sid, hrs))

        # Separate rooms by type
        self.lab_rooms = [r for r in rooms if r.get("is_lab")]
        self.theory_rooms = [r for r in rooms if not r.get("is_lab")]

    def generate(self, max_iterations: int = 2000) -> Tuple[List[dict], float, int, float, float]:
        """
        Generate an optimized timetable.

        Returns:
            (schedule_entries, fitness_score, hard_violations, soft_score, generation_time)
        """
        start_time = time.time()

        best_schedule = None
        best_fitness = -1
        best_hard = 999
        best_soft = 0

        # Run multiple attempts to find the best schedule
        num_attempts = min(10, max(3, max_iterations // 500))

        for attempt in range(num_attempts):
            schedule, tracker = self._greedy_construction()

            # Hill climbing optimization
            schedule, tracker = self._hill_climbing(
                schedule, tracker,
                iterations=max_iterations // num_attempts
            )

            hard_v = self._count_hard_violations(schedule)
            soft_s = self._calculate_soft_score(schedule, tracker)
            fitness = self._calculate_fitness(hard_v, soft_s)

            if fitness > best_fitness:
                best_schedule = schedule
                best_fitness = fitness
                best_hard = hard_v
                best_soft = soft_s

            # Perfect score — stop early
            if best_fitness >= 95:
                break

        generation_time = time.time() - start_time

        # Convert to dicts
        result = [entry.to_dict() for entry in best_schedule]

        return result, best_fitness, best_hard, best_soft, generation_time

    def _build_tasks(self) -> List[ScheduleTask]:
        """Create all scheduling tasks from class-subject assignments."""
        tasks = []
        for class_id, subjects in self.class_subject_map.items():
            for subject_id, hours in subjects:
                # Get eligible faculty for this subject
                eligible = self.subject_faculty_map.get(subject_id, [])
                if not eligible:
                    continue

                subject_info = self.subjects.get(subject_id, {})
                is_lab = subject_info.get("subject_type") in ("lab", "project")

                # Choose primary faculty (first in list)
                faculty_id = eligible[0]

                for _ in range(hours):
                    tasks.append(ScheduleTask(
                        class_id=class_id,
                        subject_id=subject_id,
                        faculty_id=faculty_id,
                        is_lab=is_lab,
                    ))
        return tasks

    def _greedy_construction(self) -> Tuple[List[ScheduleEntry], OccupancyTracker]:
        """
        Phase 1: Greedy construction with constraint-aware slot selection.
        Assigns tasks to the best available slot, prioritizing most constrained tasks first.
        """
        tasks = self._build_tasks()
        random.shuffle(tasks)

        # Sort by constraint tightness:
        # - Lab tasks first (fewer eligible rooms)
        # - Subjects with fewer eligible faculty
        tasks.sort(key=lambda t: (
            -int(t.is_lab),
            len(self.subject_faculty_map.get(t.subject_id, []))
        ))

        tracker = OccupancyTracker()
        schedule: List[ScheduleEntry] = []

        for task in tasks:
            best_slot = None
            best_score = -999

            # Get eligible rooms
            if task.is_lab:
                eligible_rooms = self.lab_rooms if self.lab_rooms else self.rooms
            else:
                eligible_rooms = self.theory_rooms if self.theory_rooms else self.rooms

            # Try all possible slots and score them
            slot_options = []
            for day in range(NUM_DAYS):
                for slot in range(NUM_SLOTS):
                    for room in eligible_rooms:
                        if tracker.is_available(task.faculty_id, room["id"],
                                                task.class_id, day, slot):
                            score = self._score_slot(
                                task, room["id"], day, slot, tracker
                            )
                            slot_options.append((day, slot, room["id"], score))

            if slot_options:
                # Pick the best-scored slot (with some randomness for variety)
                slot_options.sort(key=lambda x: -x[3])
                # Choose from top candidates with some randomness
                top_n = max(1, len(slot_options) // 5)
                chosen = random.choice(slot_options[:top_n])
                day, slot, room_id, _ = chosen

                entry = ScheduleEntry(
                    class_id=task.class_id,
                    subject_id=task.subject_id,
                    faculty_id=task.faculty_id,
                    room_id=room_id,
                    day=day,
                    time_slot=slot,
                )
                schedule.append(entry)
                tracker.occupy(task.faculty_id, room_id, task.class_id,
                              task.subject_id, day, slot)
            else:
                # Fallback: force assign to any slot (will create violations)
                day = random.randint(0, NUM_DAYS - 1)
                slot = random.randint(0, NUM_SLOTS - 1)
                room_id = random.choice(self.rooms)["id"]
                entry = ScheduleEntry(
                    class_id=task.class_id,
                    subject_id=task.subject_id,
                    faculty_id=task.faculty_id,
                    room_id=room_id,
                    day=day,
                    time_slot=slot,
                )
                schedule.append(entry)
                tracker.occupy(task.faculty_id, room_id, task.class_id,
                              task.subject_id, day, slot)

        return schedule, tracker

    def _score_slot(self, task: ScheduleTask, room_id: int,
                    day: int, slot: int, tracker: OccupancyTracker) -> float:
        """Score a potential slot assignment based on soft constraints."""
        score = 50.0  # Base score

        # S1: Prefer fewer gaps for the class
        class_lectures = tracker.get_class_lectures_on_day(task.class_id, day)
        if class_lectures > 0 and class_lectures < 5:
            score += 10  # Cluster classes together
        if class_lectures >= 5:
            score -= 15  # Too many on one day

        # S2: Limit continuous lectures for faculty
        faculty_load = tracker.get_faculty_lectures_on_day(task.faculty_id, day)
        faculty_max = self.faculty.get(task.faculty_id, {}).get("max_hours_per_day", 6)
        if faculty_load >= faculty_max:
            score -= 30  # Exceeds daily limit
        elif faculty_load >= faculty_max - 1:
            score -= 10  # Near limit

        # S3: Prefer spreading subjects across days
        if tracker.get_subject_count_on_day(task.class_id, task.subject_id, day) > 0:
            score -= 20  # Same subject twice in a day is bad

        # S4: Prefer morning slots for theory, afternoon for labs
        if task.is_lab and slot >= 3:  # Afternoon slots
            score += 5
        elif not task.is_lab and slot < 3:  # Morning slots
            score += 5

        # S5: Avoid Saturday overload (keep it light)
        if day == 5:  # Saturday
            if class_lectures >= 2:
                score -= 15

        # S6: Prefer first few days of the week
        if day <= 3:
            score += 3

        return score

    def _hill_climbing(self, schedule: List[ScheduleEntry],
                       tracker: OccupancyTracker,
                       iterations: int = 500) -> Tuple[List[ScheduleEntry], OccupancyTracker]:
        """
        Phase 2: Hill climbing optimization.
        Iteratively swaps conflicting or suboptimal slots to improve fitness.
        """
        if len(schedule) < 2:
            return schedule, tracker

        current_hard = self._count_hard_violations(schedule)
        current_soft = self._calculate_soft_score(schedule, tracker)
        current_fitness = self._calculate_fitness(current_hard, current_soft)

        no_improvement_count = 0
        max_no_improvement = iterations // 4

        for i in range(iterations):
            # Pick two random entries to swap
            idx1, idx2 = random.sample(range(len(schedule)), 2)
            e1, e2 = schedule[idx1], schedule[idx2]

            # Release both
            tracker.release(e1.faculty_id, e1.room_id, e1.class_id,
                          e1.subject_id, e1.day, e1.time_slot)
            tracker.release(e2.faculty_id, e2.room_id, e2.class_id,
                          e2.subject_id, e2.day, e2.time_slot)

            # Swap day and time_slot
            old_d1, old_s1, old_r1 = e1.day, e1.time_slot, e1.room_id
            old_d2, old_s2, old_r2 = e2.day, e2.time_slot, e2.room_id

            e1.day, e1.time_slot, e1.room_id = old_d2, old_s2, old_r2
            e2.day, e2.time_slot, e2.room_id = old_d1, old_s1, old_r1

            # Re-occupy
            tracker.occupy(e1.faculty_id, e1.room_id, e1.class_id,
                         e1.subject_id, e1.day, e1.time_slot)
            tracker.occupy(e2.faculty_id, e2.room_id, e2.class_id,
                         e2.subject_id, e2.day, e2.time_slot)

            # Evaluate
            new_hard = self._count_hard_violations(schedule)
            new_soft = self._calculate_soft_score(schedule, tracker)
            new_fitness = self._calculate_fitness(new_hard, new_soft)

            if new_fitness > current_fitness:
                # Accept the swap
                current_fitness = new_fitness
                current_hard = new_hard
                current_soft = new_soft
                no_improvement_count = 0
            else:
                # Revert the swap
                tracker.release(e1.faculty_id, e1.room_id, e1.class_id,
                              e1.subject_id, e1.day, e1.time_slot)
                tracker.release(e2.faculty_id, e2.room_id, e2.class_id,
                              e2.subject_id, e2.day, e2.time_slot)

                e1.day, e1.time_slot, e1.room_id = old_d1, old_s1, old_r1
                e2.day, e2.time_slot, e2.room_id = old_d2, old_s2, old_r2

                tracker.occupy(e1.faculty_id, e1.room_id, e1.class_id,
                             e1.subject_id, e1.day, e1.time_slot)
                tracker.occupy(e2.faculty_id, e2.room_id, e2.class_id,
                             e2.subject_id, e2.day, e2.time_slot)

                no_improvement_count += 1

            # Early termination if stuck
            if no_improvement_count >= max_no_improvement:
                break

            # Perfect score early exit
            if current_fitness >= 98:
                break

        return schedule, tracker

    def _count_hard_violations(self, schedule: List[ScheduleEntry]) -> int:
        """Count the number of hard constraint violations."""
        violations = 0

        # Build slot occupation maps
        faculty_map: Dict[Tuple[int, int, int], int] = {}  # (fid, day, slot) -> count
        room_map: Dict[Tuple[int, int, int], int] = {}     # (rid, day, slot) -> count
        class_map: Dict[Tuple[int, int, int], int] = {}    # (cid, day, slot) -> count

        for entry in schedule:
            # C1: Faculty conflict
            fkey = (entry.faculty_id, entry.day, entry.time_slot)
            faculty_map[fkey] = faculty_map.get(fkey, 0) + 1
            if faculty_map[fkey] > 1:
                violations += 1

            # C2: Room conflict
            rkey = (entry.room_id, entry.day, entry.time_slot)
            room_map[rkey] = room_map.get(rkey, 0) + 1
            if room_map[rkey] > 1:
                violations += 1

            # C3: Class conflict
            ckey = (entry.class_id, entry.day, entry.time_slot)
            class_map[ckey] = class_map.get(ckey, 0) + 1
            if class_map[ckey] > 1:
                violations += 1

        return violations

    def _calculate_soft_score(self, schedule: List[ScheduleEntry],
                               tracker: OccupancyTracker) -> float:
        """
        Calculate soft constraint satisfaction score (0-100).
        Higher is better.
        """
        if not schedule:
            return 0.0

        total_score = 0.0
        max_score = 0.0

        # ── S1: Faculty workload balance (25 pts) ──
        max_score += 25
        faculty_daily_loads: Dict[int, List[int]] = {}
        for entry in schedule:
            if entry.faculty_id not in faculty_daily_loads:
                faculty_daily_loads[entry.faculty_id] = [0] * NUM_DAYS
            faculty_daily_loads[entry.faculty_id][entry.day] += 1

        if faculty_daily_loads:
            balance_scores = []
            for fid, loads in faculty_daily_loads.items():
                max_h = self.faculty.get(fid, {}).get("max_hours_per_day", 6)
                over_limit = sum(1 for l in loads if l > max_h)
                variance = self._variance(loads)
                # Penalize over-limit and high variance
                f_score = max(0, 1.0 - over_limit * 0.3 - variance * 0.05)
                balance_scores.append(f_score)
            total_score += 25 * (sum(balance_scores) / len(balance_scores))

        # ── S2: Continuous lecture limit (25 pts) ──
        max_score += 25
        continuous_penalty = 0
        continuous_checks = 0
        for fid in faculty_daily_loads:
            for day in range(NUM_DAYS):
                consecutive = 0
                for slot in range(NUM_SLOTS):
                    if tracker.faculty_slots.get((fid, day, slot)):
                        consecutive += 1
                        if consecutive > 2:
                            continuous_penalty += 1
                    else:
                        consecutive = 0
                continuous_checks += 1
        if continuous_checks > 0:
            cont_score = max(0, 1.0 - continuous_penalty / max(1, continuous_checks) * 2)
            total_score += 25 * cont_score

        # ── S3: Class daily load balance (25 pts) ──
        max_score += 25
        class_daily_loads: Dict[int, List[int]] = {}
        for entry in schedule:
            if entry.class_id not in class_daily_loads:
                class_daily_loads[entry.class_id] = [0] * NUM_DAYS
            class_daily_loads[entry.class_id][entry.day] += 1

        if class_daily_loads:
            class_balance = []
            for cid, loads in class_daily_loads.items():
                variance = self._variance(loads)
                c_score = max(0, 1.0 - variance * 0.04)
                class_balance.append(c_score)
            total_score += 25 * (sum(class_balance) / len(class_balance))

        # ── S4: Subject spread across week (25 pts) ──
        max_score += 25
        subject_spread_scores = []
        for class_id, subjects in self.class_subject_map.items():
            for subject_id, hours in subjects:
                days_used = set()
                for entry in schedule:
                    if entry.class_id == class_id and entry.subject_id == subject_id:
                        days_used.add(entry.day)
                # More spread = better
                if hours > 0:
                    spread = len(days_used) / min(hours, NUM_DAYS)
                    subject_spread_scores.append(min(1.0, spread))
        if subject_spread_scores:
            total_score += 25 * (sum(subject_spread_scores) / len(subject_spread_scores))

        return round(total_score, 2) if max_score > 0 else 0.0

    def _calculate_fitness(self, hard_violations: int, soft_score: float) -> float:
        """
        Calculate overall fitness score (0-100).
        Hard violations drastically reduce fitness.
        """
        if hard_violations > 0:
            # Each hard violation reduces fitness significantly
            hard_penalty = min(50, hard_violations * 15)
            return max(0, 50 - hard_penalty + soft_score * 0.3)
        else:
            # No hard violations: fitness is between 50-100 based on soft score
            return 50 + soft_score * 0.5

    @staticmethod
    def _variance(data: List[int]) -> float:
        """Calculate variance of a list of integers."""
        if not data:
            return 0.0
        mean = sum(data) / len(data)
        return sum((x - mean) ** 2 for x in data) / len(data)


# ═══════════════════════════════════════════════════════════
#  CONFLICT DETECTION (for post-generation analysis)
# ═══════════════════════════════════════════════════════════

def detect_conflicts(schedule: List[dict]) -> List[dict]:
    """
    Analyze a generated schedule and return list of conflicts.
    Each conflict contains: type, severity, description, entries involved.
    """
    conflicts = []

    faculty_slots = {}
    room_slots = {}
    class_slots = {}

    for entry in schedule:
        fkey = (entry["faculty_id"], entry["day"], entry["time_slot"])
        rkey = (entry["room_id"], entry["day"], entry["time_slot"])
        ckey = (entry["class_id"], entry["day"], entry["time_slot"])

        # Check faculty conflict
        if fkey in faculty_slots:
            conflicts.append({
                "type": "Faculty Overlap",
                "severity": "high",
                "description": f"Faculty is assigned to two classes at the same time on {DAYS[entry['day']]} at {TIME_SLOTS[entry['time_slot']]}",
                "entries": [faculty_slots[fkey], entry],
            })
        else:
            faculty_slots[fkey] = entry

        # Check room conflict
        if rkey in room_slots:
            conflicts.append({
                "type": "Room Double-Booking",
                "severity": "high",
                "description": f"Room is double-booked on {DAYS[entry['day']]} at {TIME_SLOTS[entry['time_slot']]}",
                "entries": [room_slots[rkey], entry],
            })
        else:
            room_slots[rkey] = entry

        # Check class conflict
        if ckey in class_slots:
            conflicts.append({
                "type": "Class Overlap",
                "severity": "high",
                "description": f"Class has two subjects at the same time on {DAYS[entry['day']]} at {TIME_SLOTS[entry['time_slot']]}",
                "entries": [class_slots[ckey], entry],
            })
        else:
            class_slots[ckey] = entry

    return conflicts
