from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import  NumberOfCustomersForm
from .models import CustomerArrival
import random
from datetime import timedelta
from .add_to_excel import save_data_to_excel
from .get_probability import generate_service_time_table,get_avarge_waiting_time_for_custumer,generate_probability_table,get_expected_service_time,get_probability_server_idel,get_probability_that_customer_waits,get_probability_server2_idel
from datetime import timedelta

def index(request):
    return render(request,'index.html')
def add_customers(request,server_id):

    if request.method == "POST":

        form = NumberOfCustomersForm(request.POST)
        if form.is_valid():
            number_of_customers = form.cleaned_data['number_of_customers']
            max_serves_time = form.cleaned_data['max_serves_time']
            max_arrived_time = form.cleaned_data['max_arrived_time']
            print(max_arrived_time)
            try:
                if server_id==2:
                    max_serves2_time = form.cleaned_data['max_serves2_time']
                else:
                    max_serves2_time=None


                customer_arrival = CustomerArrival.objects.create(
                    number_of_customers=number_of_customers,
                    max_serves_time=max_serves_time,
                    max_arrived_time=max_arrived_time,
                    max_serves2_time=max_serves2_time
                )
            except Exception as e:print(e)
            print(customer_arrival)
            if server_id==1:

                return redirect('details_server1')
            else:
                return redirect('details_server2')
    else:

        form = NumberOfCustomersForm()

    return render(request, 'add_number_of_customers.html', {'form': form,'server_id':server_id})

def calculate_arrival_probability(probability_of_time_between_arrivals):
    arrival_probability = {
        'time_between_arrivals': probability_of_time_between_arrivals['time_between_arrivals'],
        'probability': probability_of_time_between_arrivals['probability'],
        'cumulative_probability': [],
        'random_digit_assignment': []  # list of tuples (to , from)
    }

    for time in arrival_probability['time_between_arrivals']:
        iterator = len(arrival_probability['cumulative_probability'])

        if iterator == 0:  # أول صف
            arrival_probability['cumulative_probability'].append(round(arrival_probability['probability'][iterator], 2))
            min_value = 1
            max_value = round(arrival_probability['cumulative_probability'][iterator] * 100)

            random_digit_assignment = (min_value, max_value)
            arrival_probability['random_digit_assignment'].append(random_digit_assignment)
            continue

        cumulative_probability = round(
            arrival_probability['probability'][iterator] + arrival_probability['cumulative_probability'][iterator - 1],
            2)
        arrival_probability['cumulative_probability'].append(cumulative_probability)

        min_value = round(arrival_probability['random_digit_assignment'][iterator - 1][1] + 1)
        max_value = round(arrival_probability['cumulative_probability'][iterator] * 100)

        random_digit_assignment = (min_value, max_value)
        arrival_probability['random_digit_assignment'].append(random_digit_assignment)

    return arrival_probability


def calculate_server_01(probability_of_service_time):
    server_01 = {
        'service_time': probability_of_service_time['service_time'],
        'probability': probability_of_service_time['probability'],
        'cumulative_probability': [],
        'random_digit_assignment': []  # list of tuples (to , from)
    }

    for time in server_01['service_time']:
        iterator = len(server_01['cumulative_probability'])

        if iterator == 0:  # أول صف
            server_01['cumulative_probability'].append(round(server_01['probability'][iterator], 2))
            min_value = 1
            max_value = round(server_01['cumulative_probability'][iterator] * 100)

            random_digit_assignment = (min_value, max_value)
            server_01['random_digit_assignment'].append(random_digit_assignment)
            continue

        cumulative_probability = round(
            server_01['probability'][iterator] + server_01['cumulative_probability'][iterator - 1], 2)
        server_01['cumulative_probability'].append(cumulative_probability)

        min_value = round(server_01['random_digit_assignment'][iterator - 1][1] + 1)
        max_value = round(server_01['cumulative_probability'][iterator] * 100)

        random_digit_assignment = (min_value, max_value)
        server_01['random_digit_assignment'].append(random_digit_assignment)

    return server_01


def get_simulation_table(arrival_probability, server_01, num_of_customers, opening_clock):
    opening = timedelta(hours=opening_clock)
    arrival_max_random_interval = arrival_probability['random_digit_assignment'][-1][-1]
    server_max_random_interval = server_01['random_digit_assignment'][-1][-1]

    simulation_table = {
        "cust_id": [i for i in range(1, num_of_customers + 1)],
        "random_interval": [random.randint(1, arrival_max_random_interval) for _ in range(num_of_customers)],
        "interval_time": [],
        "arrival_clock": [],
        'server_random': [random.randint(1, server_max_random_interval) for _ in range(num_of_customers)],
        "start": [],
        "duration": [],
        "end": [],
        "cust_Waiting": [],
        "server_ideal": [],
        "time_customer_spends_in_system": []
    }

    def get_interval_time(random_interval, arrival_probability):
        for index, interval in enumerate(arrival_probability["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return arrival_probability["time_between_arrivals"][index]

    def get_service_duration(random_interval, server_01):
        for index, interval in enumerate(server_01["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return server_01["service_time"][index]

    def timedelta_to_str(td):
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}"

    for index, id in enumerate(simulation_table['cust_id']):
        #  interval_time
        interval_time = get_interval_time(simulation_table['random_interval'][index], arrival_probability)
        simulation_table['interval_time'].append(interval_time)

        # service duration
        duration = get_service_duration(simulation_table['server_random'][index], server_01)
        simulation_table['duration'].append(duration)

        if id == 1:
            # arrival_clock
            arrival_clock = timedelta(minutes=simulation_table["interval_time"][index]) + opening
            simulation_table['arrival_clock'].append(arrival_clock)

            # start
            start_time = arrival_clock
            simulation_table['start'].append(start_time)

            # end
            end = simulation_table['start'][index] + timedelta(minutes=simulation_table['duration'][index])
            simulation_table['end'].append(end)

            # waiting
            simulation_table['cust_Waiting'].append(0)

            # sever ideal
            server_ideal = int(((simulation_table['arrival_clock'][index] - opening).total_seconds()) // 60)
            simulation_table['server_ideal'].append(server_ideal)

            # time custumer spends in system
            time_spent_in_system = simulation_table['duration'][index] + simulation_table['cust_Waiting'][index]
            simulation_table['time_customer_spends_in_system'].append(time_spent_in_system)
            continue

        # arrival clock
        arrival_clock = timedelta(minutes=simulation_table['interval_time'][index]) + simulation_table['arrival_clock'][
            index - 1]
        simulation_table['arrival_clock'].append(arrival_clock)

        # start
        start_time = max(simulation_table['arrival_clock'][index], simulation_table['end'][index - 1])
        simulation_table['start'].append(start_time)

        # end
        end = simulation_table['start'][index] + timedelta(minutes=simulation_table['duration'][index])
        simulation_table['end'].append(end)

        # waiting
        waiting_time = int(
            ((simulation_table['start'][index] - simulation_table['arrival_clock'][index]).total_seconds()) // 60)
        simulation_table['cust_Waiting'].append(waiting_time)

        # sever ideal
        server_ideal = int(
            ((simulation_table['start'][index] - simulation_table['end'][index - 1]).total_seconds()) // 60)
        simulation_table['server_ideal'].append(server_ideal)

        # time custumer spends in system
        time_spent_in_system = simulation_table['duration'][index] + simulation_table['cust_Waiting'][index]
        simulation_table['time_customer_spends_in_system'].append(time_spent_in_system)

    simulation_table['arrival_clock'] = [timedelta_to_str(td) for td in simulation_table['arrival_clock']]
    simulation_table['start'] = [timedelta_to_str(td) for td in simulation_table['start']]
    simulation_table['end'] = [timedelta_to_str(td) for td in simulation_table['end']]

    return simulation_table




get_simulation_table_graph=[]

def one_serves(request):


    all_data = CustomerArrival.objects.last()
    if all_data==None:
        return redirect('add_customers',1)

    probability_of_time_between_arrivals=generate_probability_table(all_data)

    probability_of_service_time = generate_service_time_table(all_data.max_serves_time)

    num_of_customers = int(all_data.number_of_customers)  # اى رقم شغال
    open_clock = 8
    arrival_probability = calculate_arrival_probability(probability_of_time_between_arrivals)
    server_01 = calculate_server_01(probability_of_service_time)
    simulation_table = get_simulation_table(arrival_probability, server_01, num_of_customers, open_clock)
    # كلو لأما intger / float
    get_simulation_table_graph.append(simulation_table)

    avarge_waiting_time_for_custumer = get_avarge_waiting_time_for_custumer(simulation_table)
    probability_that_a_customer_wait = get_probability_that_customer_waits(simulation_table)
    probability_server_idel = get_probability_server_idel(simulation_table)
    expected_service_time = get_expected_service_time(server_01)

    save_data_to_excel(fr"media\excel_file\simulation_data.xlsx", arrival_probability, server_01, simulation_table)

    CustomerArrival.objects.all().delete()

    return render(request,'server1.html',
 {
            'arrival_probability_table':list(zip(*arrival_probability.values())),
            'keys1':arrival_probability.keys(),
            'servers_table':list(zip(*server_01.values())),
            'keys2':server_01.keys(),
            'simulation_table':list(zip(*simulation_table.values())),
            'keys3':simulation_table.keys(),
            'avarge_waiting_time_for_custumer':avarge_waiting_time_for_custumer,
            'probability_that_a_customer_wait':probability_that_a_customer_wait,
            'probability_server_idel':probability_server_idel,
            'expected_service_time':expected_service_time,
            'data1':arrival_probability,
            'data2':server_01,
            'data3':simulation_table,
        })

def render_chart(request):

    for simulation in get_simulation_table_graph:
         start_times = simulation['arrival_clock']

    for simulation in get_simulation_table_graph:
         end_times = simulation['end']

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
    print(context)
    return render(request, "graph.html", context)


#####################################################
# فنكشن بتاعتي انا لو التانيه مشتغلتش
"""def get_simulation_table2(arrival_probability, server_probs1, server_probs2, num_of_customers):
    opening = timedelta(hours=8)
    arrival_max_random_interval = arrival_probability['random_digit_assignment'][-1][-1]
    server_max_random_interval = max(server_probs1['random_digit_assignment'][-1][-1], server_probs2['random_digit_assignment'][-1][-1])

    # جدول المحاكاة
    simulation_table = {
        "cust_id": [i for i in range(1, num_of_customers + 1)],
        "random_interval": [random.randint(0, arrival_max_random_interval) for _ in range(num_of_customers)],
        "interval_time": [],
        "arrival_clock": [],
        "server_random": [random.randint(1, server_max_random_interval) for _ in range(num_of_customers)],
        "server1_start": [],
        "server1_end": [],
        "duration": [],
        "server_ideal": [],
        "server2_start": [],
        "server2_end": [],
        "server2_duration": [],
        "server2_idle": [],
        "cust_Waiting": [],
        "time_customer_spends_in_system": [],
    }

    # أوقات انتهاء السيرفرات
    server_end_times = [opening, opening]  # سيرفر1، سيرفر2

    def get_interval_time(random_interval, arrival_probability):
        for index, interval in enumerate(arrival_probability["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return arrival_probability["time_between_arrivals"][index]

    def get_service_duration(random_interval, server_probs):
        for index, interval in enumerate(server_probs["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return server_probs["service_time"][index]

    def timedelta_to_str(td):
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}"

    for index, id in enumerate(simulation_table['cust_id']):
        # interval_time
        interval_time = get_interval_time(simulation_table['random_interval'][index], arrival_probability)
        simulation_table['interval_time'].append(interval_time)

        if id == 1:
            # أول زبون يدخل
            arrival_clock = opening + timedelta(minutes=interval_time)
            simulation_table['arrival_clock'].append(arrival_clock)

            # تخصيص السيرفر الأول
            assigned_server = 0  # السيرفر الأول (server1)
            duration = get_service_duration(simulation_table['server_random'][index], server_probs1)
            server_end_times[assigned_server] = arrival_clock + timedelta(minutes=duration)

            # تعبئة بيانات السيرفر الأول
            simulation_table['server1_start'].append(arrival_clock)
            simulation_table['server1_end'].append(server_end_times[assigned_server])
            simulation_table['duration'].append(duration)
            simulation_table['server_ideal'].append(True)  # السيرفر كان في وضع خمول قبل العمل

            # السيرفر الثاني يبقى خامل
            simulation_table['server2_start'].append("")
            simulation_table['server2_end'].append("")
            simulation_table['server2_duration'].append("")
            simulation_table['server2_idle'].append(True)

            # العميل الأول لا ينتظر
            simulation_table['cust_Waiting'].append(0)

            # الوقت الذي يقضيه العميل في النظام
            simulation_table['time_customer_spends_in_system'].append(duration)
            continue

        # حساب وقت وصول العميل
        arrival_clock = simulation_table['arrival_clock'][index - 1] + timedelta(minutes=interval_time)
        simulation_table['arrival_clock'].append(arrival_clock)

        # تحديد السيرفر المتاح
        assigned_server = 0 if server_end_times[0] <= server_end_times[1] else 1

        # حساب وقت بدء الخدمة
        start_time = max(arrival_clock, server_end_times[assigned_server])
        duration = get_service_duration(simulation_table['server_random'][index],
                                         server_probs1 if assigned_server == 0 else server_probs2)
        end_time = start_time + timedelta(minutes=duration)
        server_end_times[assigned_server] = end_time

        # تعبئة بيانات السيرفر المختار
        if assigned_server == 0:
            simulation_table['server1_start'].append(start_time)
            simulation_table['server1_end'].append(end_time)
            simulation_table['duration'].append(duration)
            simulation_table['server_ideal'].append(start_time > server_end_times[0])  # السيرفر في وضع خمول
            # تعبئة بيانات السيرفر الثاني كخامل
            simulation_table['server2_start'].append("")
            simulation_table['server2_end'].append("")
            simulation_table['server2_duration'].append("")
            simulation_table['server2_idle'].append(True)
        else:
            simulation_table['server2_start'].append(start_time)
            simulation_table['server2_end'].append(end_time)
            simulation_table['server2_duration'].append(duration)
            simulation_table['server2_idle'].append(start_time > server_end_times[1])  # السيرفر في وضع خمول
            # تعبئة بيانات السيرفر الأول كخامل
            simulation_table['server1_start'].append("")
            simulation_table['server1_end'].append("")
            simulation_table['duration'].append("")
            simulation_table['server_ideal'].append(True)

        # حساب وقت الانتظار
        waiting_time = max(0, (start_time - arrival_clock).total_seconds() // 60)
        simulation_table['cust_Waiting'].append(int(waiting_time))

        # الوقت الذي يقضيه العميل في النظام
        simulation_table['time_customer_spends_in_system'].append(duration + int(waiting_time))

    # تحويل الوقت إلى نص
    for key in ['arrival_clock', 'server1_start', 'server1_end', 'server2_start', 'server2_end']:
        simulation_table[key] = [timedelta_to_str(td) if isinstance(td, timedelta) else td for td in simulation_table[key]]

    return simulation_table"""
def get_simulation_table2(arrival_probability, server_01, server_02, num_of_customers):


    opening = timedelta(hours=8)
    arrival_max_random_interval = arrival_probability['random_digit_assignment'][-1][-1]

    simulation_table = {
        "cust_id": [i for i in range(1, num_of_customers + 1)],
        "random_interval": [random.randint(1, arrival_max_random_interval) for _ in range(num_of_customers)],
        "interval_time": [],
        "arrival_clock": [],
        "server_ideal": [],
        "server2_idle": [],
        "server_random": [random.randint(1, 100) for _ in range(num_of_customers)],  # change
        "last_customer_ser_1": [],
        "last_customer_ser_2": [],
        "server1_start": [],
        "duration": [],
        "server1_end": [],
        "server2_start": [],
        "server2_duration": [],
        "server2_end": [],
        "cust_Waiting": [],
        "time_customer_spends_in_system": []
    }

    def get_interval_time(random_interval, arrival_probability):
        for index, interval in enumerate(arrival_probability["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return arrival_probability["time_between_arrivals"][index]

    def get_service_duration(random_interval, server):

        for index, interval in enumerate(server["random_digit_assignment"]):
            if random_interval <= interval[1]:
                return server["service_time"][index]

    def timedelta_to_str(td):
        hours, remainder = divmod(td.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}"

    no_time = timedelta()
    for index, id in enumerate(simulation_table['cust_id']):
        #  interval_time
        interval_time = get_interval_time(simulation_table['random_interval'][index], arrival_probability)
        simulation_table['interval_time'].append(interval_time)

        if id == 1:
            # arrival_clock
            arrival_clock = timedelta(minutes=simulation_table["interval_time"][index]) + opening
            simulation_table['arrival_clock'].append(arrival_clock)

            # idle server 1
            server_ideal = 'TRUE'
            simulation_table['server_ideal'].append(server_ideal)

            # idle server 2
            server2_idle = 'TRUE'
            simulation_table['server2_idle'].append(server2_idle)

            # last customer server 1
            simulation_table['last_customer_ser_1'].append(no_time)

            # last customer server 2
            simulation_table['last_customer_ser_2'].append(no_time)

            # start 1
            server1_start = arrival_clock
            simulation_table['server1_start'].append(server1_start)

            # duration 1
            duration = get_service_duration(simulation_table['server_random'][index], server_01)
            simulation_table['duration'].append(duration)

            # end 1
            server1_end = simulation_table['server1_start'][index] + timedelta(minutes=simulation_table['duration'][index])
            simulation_table['server1_end'].append(server1_end)

            # start 2
            simulation_table['server2_start'].append(no_time)

            # duration 2
            simulation_table['server2_duration'].append('')

            # end 2
            simulation_table['server2_end'].append(no_time)

            # waiting
            simulation_table['cust_Waiting'].append(0)

            # sever ideal
            server_ideal = int(((simulation_table['arrival_clock'][index] - opening).total_seconds()) // 60)
            simulation_table['server_ideal'].append(server_ideal)

            # time custumer spends in system
            time_spent_in_system = duration
            simulation_table['time_customer_spends_in_system'].append(time_spent_in_system)
            continue

        # arrival clock
        arrival_clock = timedelta(minutes=simulation_table['interval_time'][index]) + simulation_table['arrival_clock'][
            index - 1]
        simulation_table['arrival_clock'].append(arrival_clock)

        # last customer server 1
        last_customer_ser_1 = max(simulation_table['server1_end'])
        simulation_table['last_customer_ser_1'].append(last_customer_ser_1)

        # last customer server 2
        last_customer_ser_2 = max(simulation_table['server2_end'])
        simulation_table['last_customer_ser_2'].append(last_customer_ser_2)

        # idle server 1
        server_ideal = 'TRUE' if arrival_clock >= last_customer_ser_1 else 'FALSE'
        simulation_table['server_ideal'].append(server_ideal)

        # idle server 2
        server2_idle = 'TRUE'
        if arrival_clock < last_customer_ser_2:
            server2_idle = 'FALSE'
        simulation_table['server2_idle'].append(server2_idle)

        # start 1
        server1_start = arrival_clock
        if server2_idle == 'TRUE' and last_customer_ser_1 <= last_customer_ser_2:
            server1_start = last_customer_ser_1
        else:
            server1_start = no_time

        simulation_table['server1_start'].append(server1_start)

        # duration 1
        duration = ''
        if server1_start != no_time:
            duration = get_service_duration(simulation_table['server_random'][index], server_01)

        simulation_table['duration'].append(duration)

        # end 1
        server1_end = no_time
        if server1_start != no_time:
            server1_end = simulation_table['server1_start'][index] + timedelta(minutes=simulation_table['duration'][index])

        simulation_table['server1_end'].append(server1_end)

        # start 2
        server2_start = no_time
        if server1_start == no_time:
            server2_start = max(arrival_clock, last_customer_ser_2)
        simulation_table['server2_start'].append(server2_start)

        # duration 2
        server2_duration = ''
        if server2_start != no_time:
            server2_duration = get_service_duration(simulation_table['server_random'][index], server_02)

        simulation_table['server2_duration'].append(server2_duration)

        # end 2
        server2_end = no_time
        if server2_start != no_time:
            server2_end = simulation_table['server2_start'][index] + timedelta(minutes=simulation_table['server2_duration'][index])

        simulation_table['server2_end'].append(server2_end)

        # waiting
        waiting_time = int(((max(server1_start, server2_start) - arrival_clock).total_seconds()) // 60)
        simulation_table['cust_Waiting'].append(waiting_time)

        # time custumer spends in system
        time_spent_in_system = waiting_time + max(int(duration) if duration else 0,
                                                  int(server2_duration) if server2_duration else 0)
        simulation_table['time_customer_spends_in_system'].append(time_spent_in_system)

    return simulation_table

def details_server2(request):
    all_data = CustomerArrival.objects.last()

    if all_data == None:
        return redirect('add_customers',2)

    probability_of_time_between_arrivals = generate_probability_table(all_data)

    probability_of_service_one_time = generate_service_time_table(all_data.max_serves_time)
    probability_of_service_two_time = generate_service_time_table(all_data.max_serves2_time)

    num_of_customers = int(all_data.number_of_customers)  # اى رقم شغال

    arrival_probability = calculate_arrival_probability(probability_of_time_between_arrivals)
    server_01 = calculate_server_01(probability_of_service_one_time)
    server_02 = calculate_server_01(probability_of_service_two_time)
    simulation_table = get_simulation_table2(arrival_probability, server_01,server_02, num_of_customers)
    print(arrival_probability)
    print(server_01)
    print(server_02)
    print(simulation_table)
    # كلو لأما intger / float

    avarge_waiting_time_for_custumer = get_avarge_waiting_time_for_custumer(simulation_table)
    probability_that_a_customer_wait = get_probability_that_customer_waits(simulation_table)
    #probability_server1_idel = get_probability_server_idel(simulation_table)
    #probability_server2_idel = get_probability_server2_idel(simulation_table)
    expected_service_time = get_expected_service_time(server_01)

    save_data_to_excel(fr"media\excel_file\simulation_data.xlsx", arrival_probability, server_01, simulation_table,server_02)

    CustomerArrival.objects.all().delete()

    return render(request, 'server2.html',
                  {
                      'arrival_probability_table': list(zip(*arrival_probability.values())),
                      'keys1': arrival_probability.keys(),
                      'servers_table': list(zip(*server_01.values())),
                      'keys2': server_01.keys(),
                      'simulation_table': list(zip(*simulation_table.values())),
                      'keys3': simulation_table.keys(),
                      'avarge_waiting_time_for_custumer': avarge_waiting_time_for_custumer,
                      'probability_that_a_customer_wait': probability_that_a_customer_wait,

                      'expected_service_time': expected_service_time,
                      'data1': arrival_probability,
                      'data2': server_01,
                      'data4': server_02,
                      'data3': simulation_table,
                  })