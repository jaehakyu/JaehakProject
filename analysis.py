import pandas as pd

jumpman = pd.read_csv('jumpman.csv')

#Checking to see if a delivery is within an overall package/same-delivery

def same_delivery():
    same_deliveries = []
    logged = []
    for i in jumpman.delivery_id:
        index = jumpman[jumpman.delivery_id == i].index.tolist()
        if i in logged:
            logged = logged
        else:
            if len(index) > 1:
                same_deliveries += index[1-len(index):]
                logged.append(i)
    return same_deliveries

same_deliveries = same_delivery()

def new_column():
    delivery_status = []
    for i in range(0,len(jumpman)):
        if i in same_deliveries:
            delivery_status.append('Same Delivery')
        else:
            delivery_status.append('Unique')
    return delivery_status

status = new_column()
jumpman['same_delivery'] = status

#Creating a list of unique delivery instances
deduped_jumpman = jumpman.drop(same_deliveries)

#Breakouts by geography

boroughs = sorted(set(deduped_jumpman.dropoff_borough))
dates = sorted(set(deduped_jumpman.delivery_start_date))
hoods = sorted(set(deduped_jumpman.dropoff_hood))

def counter(check_col, count_col, checklist):
    average = []
    for i in checklist:
        x = deduped_jumpman[count_col][jumpman[check_col] == i].count()
        average.append(x)
    return pd.DataFrame(average, checklist)

orders_by_drop_borough = counter('dropoff_borough', 'dropoff_borough',boroughs)
orders_by_day = counter('delivery_start_date', 'delivery_id', dates)
orders_by_drop_hood = counter('dropoff_hood', 'delivery_id', hoods)

#Calculating distances b/n pickup & dropoff
#Formula courtesy of: https://gist.github.com/rochacbruno/2883505

import math

def distance_count():
    def distance(origin, destination):
        lat1, lon1 = origin.split(', ')[0], origin.split(', ')[1]
        lat2, lon2 = destination.split(', ')[0], destination.split(', ')[1]
        radius = 3959 #miles
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = radius * c
        return d
    distances = []
    for i in deduped_jumpman.index:
        distances.append(distance(deduped_jumpman.pickup_coordinate[i], deduped_jumpman.dropoff_coordinate[i]))
    return distances

deduped_jumpman['delivery_distance'] = distance_count()

#Calculating averages of distances

import numpy as np

#Note that the average distance is 1.13 miles
average_distance = np.sum(deduped_jumpman.delivery_distance,axis=0)/len(deduped_jumpman)

#Note that 58% of users order from restaurants within a mile
within_mile_pct = deduped_jumpman.delivery_distance[deduped_jumpman.delivery_distance < 1].count()/len(deduped_jumpman)

#Analyzing frequencies of repeat orders
#Note that the below shows that there are 3192 unique customers
#Of that, 976 were repeat customers

customers = set(jumpman.customer_id)
customers = sorted(customers)
repeat_count = deduped_jumpman.customer_id.value_counts()

#Analyzing likelihood of ordering from the same store/restaurant
#Analyzing likelihood of ordering from same category
#Analyzing likelihood of ordering from the same address

repeat_offenders = list(repeat_count.index[repeat_count > 1])

def repeat_checkers():
    re_repeaters = 0
    category_repeaters = 0
    loc_repeaters = 0
    for i in repeat_offenders:
        places = []
        cats = []
        loc = []
        index = deduped_jumpman[deduped_jumpman.customer_id == i].index.tolist()
        for x in index:
            places.append(deduped_jumpman.pickup_place[x])
            cats.append(deduped_jumpman.place_category[x])
            loc.append(deduped_jumpman.dropoff_coordinate[x])
        if len(places)/len(set(places)) != 1:
            re_repeaters += 1
        if len(cats)/len(set(cats)) != 1:
            category_repeaters += 1
        if len(loc)/len(set(loc)) != 1:
            loc_repeaters += 1
    return re_repeaters, category_repeaters, loc_repeaters

#Converting times

from datetime import datetime

def time_converter(x):
    try:
        time_one = datetime.strptime(x, '%H:%M:%S.%f')
        time_two = time_one.time()
        return time_two
    except:
        return pd.NaT

deduped_jumpman.delivery_start_time = deduped_jumpman.delivery_start_time.apply(time_converter)
deduped_jumpman.pickup_arrival_time = deduped_jumpman.pickup_arrival_time.apply(time_converter)
deduped_jumpman.pickup_depart_time = deduped_jumpman.pickup_depart_time.apply(time_converter)
deduped_jumpman.dropoff_time = deduped_jumpman.dropoff_time.apply(time_converter)

jumpman.delivery_start_time = jumpman.delivery_start_time.apply(time_converter)
jumpman.pickup_arrival_time = jumpman.pickup_arrival_time.apply(time_converter)
jumpman.pickup_depart_time = jumpman.pickup_depart_time.apply(time_converter)
jumpman.dropoff_time = jumpman.dropoff_time.apply(time_converter)

#Converting dates

def date_converter(x):
    try:
        date_one = datetime.strptime(x, '%Y-%m-%d')
        date_two = date_one.date()
        return date_two
    except:
        return pd.NaT

deduped_jumpman.delivery_start_date = deduped_jumpman.delivery_start_date.apply(date_converter)
deduped_jumpman.pickup_arrival_date = deduped_jumpman.pickup_arrival_date.apply(date_converter)
deduped_jumpman.pickup_depart_date = deduped_jumpman.pickup_depart_date.apply(date_converter)
deduped_jumpman.dropoff_date = deduped_jumpman.dropoff_date.apply(date_converter)

jumpman.delivery_start_date = jumpman.delivery_start_date.apply(date_converter)
jumpman.pickup_arrival_date = jumpman.pickup_arrival_date.apply(date_converter)
jumpman.pickup_depart_date = jumpman.pickup_depart_date.apply(date_converter)
jumpman.dropoff_date = jumpman.dropoff_date.apply(date_converter)

#Breaking out dates into weeks

def week_maker():
    weeks = []
    for i in jumpman.delivery_start_date:
        if i.day <= 5:
            weeks.append('Week 1')
        elif i.day <= 12:
            weeks.append('Week 2')
        elif i.day <= 19:
            weeks.append('Week 3')
        else:
            weeks.append('Week 4')
    return weeks

#Calculating driver retention

jumpman['week'] = week_maker()

def week_jumpers():
    index1 = jumpman[jumpman.week == 'Week 1'].index.tolist()
    index2 = jumpman[jumpman.week == 'Week 2'].index.tolist()
    index3 = jumpman[jumpman.week == 'Week 3'].index.tolist()
    index4 = jumpman[jumpman.week == 'Week 4'].index.tolist()
    week1_jumpers = jumpman.jumpman_id[index1]
    week2_jumpers = jumpman.jumpman_id[index2]
    week3_jumpers = jumpman.jumpman_id[index3]
    week4_jumpers = jumpman.jumpman_id[index4]
    uniques1 = set(week1_jumpers)
    uniques2 = set(week2_jumpers)
    uniques3 = set(week3_jumpers)
    uniques4 = set(week4_jumpers)
    jumpers = set(jumpman.jumpman_id)
    count_check = []
    for i in jumpers:
        count = 0
        if i in uniques1:
            count += 1
        if i in uniques2:
            count += 1
        if i in uniques3:
            count += 1
        if i in uniques4:
            count += 1
        count_check.append(count)
    return pd.DataFrame(count_check, jumpers)

repeat_jumpers = week_jumpers()

#Identifying if people purchase at the same time

def time_checkers():
    time_diff = []
    for i in repeat_offenders:
        index = deduped_jumpman[deduped_jumpman.customer_id == i].index.tolist()
        times = deduped_jumpman.delivery_start_time[index].tolist()
        maxtime, mintime = max(times), min(times)
        diff = maxtime.hour - mintime.hour
        time_diff.append(diff)
    return time_diff

time_repeats = time_checkers()

time_count = 0
for i in time_repeats:
    if i <= 3:
        time_count += 1

window = time_count/len(time_repeats)

#Computing average number of orders per day

dates = sorted(set(jumpman.delivery_start_date))

def daily_orders():
    average = []
    for i in dates:
        x = jumpman.delivery_id[jumpman.delivery_start_date == i].count()
        average.append(x)
    return pd.DataFrame(average,dates)

group = daily_orders()

#Adding in a column for delivery start time hours to see when deliveries
#are most popular
hours = []
for i in deduped_jumpman.delivery_start_time:
    hours.append(i.hour)

deduped_jumpman['delivery_start_hour'] = hours

def hourly_orders():
    average = []
    all_hours = sorted(set(deduped_jumpman.delivery_start_hour))
    for i in all_hours:
        x = deduped_jumpman.delivery_id[deduped_jumpman.delivery_start_hour == i].count()
        average.append(x)
    return pd.DataFrame(average,all_hours)

peak_hours = hourly_orders()

#Looking now at fleet health. What is the composition of the fleet?

jumpmen = sorted(set(jumpman.jumpman_id))

def jumpmen_vehicles():
    vehicles = []
    for i in jumpmen:
        index = jumpman[jumpman.jumpman_id == i].index.tolist()
        vehicles += (sorted(set(jumpman.vehicle_type[index])))
    return pd.DataFrame(jumpmen, vehicles)

jumpmen_by_vehicles = jumpmen_vehicles()

#Now looking at average delivery times for each jumpman

def from_pickup():
    times = []
    for i in range(0,len(jumpman)):
        x = jumpman.pickup_depart_time[i].hour + (jumpman.pickup_depart_time[i].minute/60)
        times.append(x)
    return times

def arrival():
    times = []
    for i in range(0,len(jumpman)):
        x = jumpman.dropoff_time[i].hour + (jumpman.dropoff_time[i].minute/60)
        times.append(x)
    return times

def duration_calc():
    times = []
    x = from_pickup()
    y = arrival()
    for i in range(0,len(x)):
        if x[i] > y[i]:
            z = ((y[i]+24)-x[i])*60
            times.append(z)
        else:
            z = (y[i] - x[i])*60
            times.append(z)
    return times

jumpman['delivery_duration'] = duration_calc()

def durations_by_vehicle():
    average = []
    vehicles = sorted(set(jumpman.vehicle_type))
    for i in vehicles:
        x = jumpman.delivery_duration[jumpman.vehicle_type == i].sum()/jumpman.delivery_duration[jumpman.vehicle_type == i].count()
        average.append(x)
    return pd.DataFrame(average,vehicles)
