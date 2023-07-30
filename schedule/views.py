from django.shortcuts import render, redirect
from .models import Assignment
import pydantic
import time
import json
from datetime import date, timedelta
from .utils import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    # check if post request to add assignment
    if request.method == "POST":
        if "name" in request.POST:
            name = request.POST["name"]
            start_date = request.POST["start_date"]
            end_date = request.POST["end_date"]
            work_load = request.POST["work_load"]

            assignment = Assignment(
                name=name, start_date=start_date, end_date=end_date, work_load=work_load, user=request.user
            )
            assignment.save()

            return redirect(index)
        elif "delete" in request.POST:
            name = request.POST["delete"]
            assignment = Assignment.objects.get(name=name, user=request.user)
            assignment.delete()

            return redirect(index)
        elif "username" in request.POST:
            username = request.POST["username"]
            password = request.POST["password"]

            user = authenticate(request, username=username, password=password) 

            if user is not None:
                login(request, user)

            return redirect(index)
        else:
            for a in json.loads(request.POST["assignments"]):
                assignment = Assignment.objects.get(name=a["name"], user=request.user)

                assignment.work_load = a["work_load"]
                assignment.save()

            return redirect(index)

    if not request.user.is_authenticated:
        return render(request, "schedule/login.html")

    assignments = Assignment.objects.filter(user=request.user)
    if len(assignments) == 0:
        return render(request, "schedule/index.html")

    schedule = optimize_schedule(assignments, 100)

    (
        labels,
        total,
        date_list,
        today_chart_labels,
        today_chart_data,
        line_chart_data,
    ) = ([], 0, [], [], [], {})
    if date.today() in schedule.days:
        total = int(schedule.days[date.today()].total_work * 60)
        min_start_date = min([assignment.start_date for assignment in assignments])
        min_start_date = max(min_start_date, date.today())
        max_end_date = max([assignment.end_date for assignment in assignments])

        date_list = [
            min_start_date + timedelta(days=x)
            for x in range((max_end_date - min_start_date).days + 1)
        ]
        for d in date_list:
            labels.append(d.strftime("%B %-d"))

        today_chart_labels = []
        today_chart_data = []

        for assignment in assignments:
            try:
                today_chart_data.append(
                    int(schedule.days[date.today()].work_load[assignment] * 60)
                )
                today_chart_labels.append(assignment.name)
            except KeyError:
                pass

            line_chart_data[assignment.name] = []
            for d in date_list:
                try:
                    line_chart_data[assignment.name].append(
                        int(schedule.days[d].work_load[assignment] * 60)
                    )
                except KeyError as e:
                    line_chart_data[assignment.name].append(0)

    return render(
        request,
        "schedule/index.html",
        {
            "line_chart_data": line_chart_data,
            "labels": labels,
            "total": total,
            "today_chart_labels": today_chart_labels,
            "today_chart_data": today_chart_data,
            "assignments": assignments,
        },
    )
