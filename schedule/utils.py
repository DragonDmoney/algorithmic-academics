import pydantic
from typing import Dict, List
from datetime import date, timedelta
from .models import Assignment

MIN_WORK = 0.5

class Day(pydantic.BaseModel):
    date: date
    work_load: Dict[Assignment, float]

    @property
    def total_work(self) -> float:
        return sum(self.work_load.values())

    class Config:
        arbitrary_types_allowed = True


class Schedule(pydantic.BaseModel):
    days: Dict[date, Day]


def optimize_schedule(assignments: List[Assignment], iterations: int) -> Schedule:
    min_start_date = max(
        min(assignment.start_date for assignment in assignments), date.today()
    )
    max_end_date = max(assignment.end_date for assignment in assignments)
    total_days = (max_end_date - min_start_date).days

    schedule = Schedule(
        days={
            min_start_date
            + timedelta(days=x): Day(
                date=min_start_date + timedelta(days=x), work_load={}
            )
            for x in range(total_days)
        }
    )

    for assignment in assignments:
        schedule.days[max(assignment.start_date, date.today())].work_load[
            assignment
        ] = assignment.work_load

    for _ in range(iterations):
        for day, day_obj in schedule.days.items():
            for assignment, work in list(day_obj.work_load.items()):
                for d in (
                    assignment.start_date + timedelta(days=x)
                    for x in range((assignment.end_date - assignment.start_date).days)
                ):
                    diff = day_obj.total_work - schedule.days[max(d, date.today())].total_work

                    amt = min(work, diff / 2)
                    amt = min(amt, schedule.days[day].work_load[assignment]-MIN_WORK) 

                    if amt > 0.05 and schedule.days[max(d, date.today())].work_load.get(assignment, 0) + amt > MIN_WORK:
                        # if schedule.days[day].work_load[assignment] < MAX_WORK:
                        #     amt = min(amt, MAX_WORK-schedule.days[d].work_load.get(assignment, 0))

                        day_obj.work_load[assignment] -= amt
                        schedule.days[max(d, date.today())].work_load[assignment] = (
                            schedule.days[max(d, date.today())].work_load.get(assignment, 0) + amt
                        )

                        # print(f"moving {amt} from {day} to {d} {schedule.days[day].work_load[assignment]} {schedule.days[d].work_load[assignment]}")
                        # print(schedule.days[test_date].total_work)

                        break

    return schedule
