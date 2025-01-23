import random
import numpy as np

def get_avarge_waiting_time_for_custumer(simulation_table):
    total_waiting = 0
    for time in simulation_table['cust_Waiting']:
        total_waiting += time

    return round(total_waiting / len(simulation_table['cust_Waiting']), 2)


def get_probability_that_customer_waits(simulation_table):
    waiting_count = 0
    for cust_wait in simulation_table['cust_Waiting']:
        if cust_wait > 0:
            waiting_count += 1
    return round(waiting_count / len(simulation_table['cust_Waiting']), 2)


def get_probability_server_idel(simulation_table):
    total_ideal = 0
    for server in simulation_table['server_ideal']:
        try:
            print(simulation_table['server_ideal'])
            total_ideal += server
        except:pass


    total_duration_time = 0
    for time in simulation_table['duration']:
        print(time)
        if time!='':
            total_duration_time += (time)

    return round(total_ideal / (total_ideal + total_duration_time), 2)
def get_probability_server2_idel(simulation_table):
    total_ideal = 0
    for server in simulation_table['server2_idle']:
        total_ideal += server

    total_duration_time = 0
    for time in simulation_table['server2_duration']:
        print(simulation_table['server2_duration'])
        if time != '':
            total_duration_time += time

    return round(total_ideal / (total_ideal + total_duration_time), 2)


def get_expected_service_time(server_01):
    sum_product = 0
    for index, service_time in enumerate(server_01['service_time']):
        sum_product += service_time * server_01['probability'][index]
    return round(sum_product, 2)


# هسلمك دول ينجم
def generate_probability_table(all_data):

    time_between_arrivals =[prob for prob in range(int(all_data.max_arrived_time))]
    raw_probabilities = np.random.dirichlet(np.ones(int(all_data.max_arrived_time))).tolist()

    probabilities = [max(0, round(prob, 2)) for prob in raw_probabilities]

    total_prob = sum(probabilities)
    diff = 1 - total_prob


    if diff != 0:

        for i in range(len(probabilities)):

            probabilities[i] += round(diff / len(probabilities), 2)

        total_prob = sum(probabilities)
        diff = 1 - total_prob
        if diff != 0:
            probabilities[0] += max(0, round(diff, 2))

    probability_of_time_between_arrivals = {
        'time_between_arrivals': time_between_arrivals,
        'probability': probabilities
    }

    print(probability_of_time_between_arrivals)
    return probability_of_time_between_arrivals


def generate_service_time_table(all_data):

    service_time = [prob for prob in range(1,int(all_data) + 1)]
    raw_probabilities = np.random.dirichlet(np.ones(int(all_data))).tolist()
    probabilities = [max(0, round(prob, 2)) for prob in raw_probabilities]

    total_prob = sum(probabilities)
    diff = 1 - total_prob

    if diff != 0:

        for i in range(len(probabilities)):
            probabilities[i] += round(diff / len(probabilities), 2)

        total_prob = sum(probabilities)
        diff = 1 - total_prob
        if diff != 0:
            probabilities[0] += max(0, round(diff, 2))

    probability_of_service_time = {
        'service_time': service_time,
        'probability': probabilities
    }
    print(probability_of_service_time)
    return probability_of_service_time