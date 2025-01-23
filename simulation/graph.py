from django.shortcuts import render



def render_chart(request):
    simulation_table = [
        {"arrival_time": 0, "end_service": 10},
        {"arrival_time": 5, "end_service": 15},
        {"arrival_time": 10, "end_service": 20},
        {"arrival_time": 15, "end_service": 25},
    ]
    simulation_table=get_simulation_table()
    # استخراج أوقات الدخول والخروج من simulation_table
    start_times = [entry["arrival_time"] for entry in simulation_table]
    end_times = [entry["end_service"] for entry in simulation_table]

    time_points = []
    for start, end in zip(start_times, end_times):
        time_points.append((start, 'enter'))
        time_points.append((end, 'leave'))

    time_points.sort()
    current_customers = 0
    customer_count_per_time = []

    for time, event in time_points:
        if event == 'enter':
            current_customers += 1
        else:
            current_customers -= 1
        customer_count_per_time.append((time, current_customers))

    times = [entry[0] for entry in customer_count_per_time]
    customers_in_system = [entry[1] for entry in customer_count_per_time]

    # تمرير البيانات إلى القالب
    context = {
        "times": times,  # المحور السيني
        "customers_in_system": customers_in_system,  # المحور الصادي
    }
    return render(request, "graph.html", context)
