import numpy as np
from numpy import random
import matplotlib.pyplot as plt
import timeit
start = timeit.default_timer()

job = 0
dormant = False
number_of_jobs = 1000
number_of_iterations = 1000
corrective_cost = 10
preventive_cost = 1


standard_deviation_parameter = 0.6
wp1 = 886
wp2 = -0.14
k = 0.4
reference_number_of_cycles = 50000

first_load = 120
second_load = 140
damage_level_limit = 0.2

if first_load < second_load:
    ing = "increasing"
else:
    ing = "decreasing"

failure_type = ''
preventive = np.zeros((1,))
corrective = np.zeros((1,))

# VIRTUAL

# ni
ni = np.full((number_of_jobs,), 1000)
# sigma
a = np.full(int(number_of_jobs / 2), first_load)
b = np.full(int(number_of_jobs / 2), second_load)
sigma = np.concatenate((a, b), axis=0)

# nf
nf_virtual = np.power(sigma / wp1, 1 / wp2)
#rk
rk_virtual = np.power(nf_virtual / reference_number_of_cycles, k)

#SAMPLED

#normal
normal_mean = np.power(sigma / wp1, 1 / wp2)  # for each sigma generates mean and variance
normal_stdev = np.power(sigma / wp1, (1 / wp2)) * standard_deviation_parameter

for i in range(0, number_of_iterations):

    # VIRTUAL

    # nei -- FOR
    nei_virtual = np.array([])
    nei_virtual = np.concatenate((nei_virtual, np.array([1000])), axis=0)
    # dk -- FOR
    dk_virtual = np.array([])
    dk_virtual_first_cell = np.power(nei_virtual[0] / nf_virtual[0], rk_virtual[0])
    dk_virtual = np.concatenate((dk_virtual, dk_virtual_first_cell.reshape((1,))), axis=0)

    # SAMPLED

    # parameters -- FOR
    nf_sampled = np.array([])
    rk_sampled = np.array([])
    nei_sampled = np.array([])
    nei_sampled = np.concatenate((nei_sampled, ni[0].reshape(1, )), axis=0)
    dk_sampled = np.zeros((1,))

    for j in range(0, number_of_jobs):

        if j > 0:

            #VIRTUAL
            # nei AND dk
            nei_virtual_new_cell = nf_virtual[j] * np.power(dk_virtual[j - 1], 1 / rk_virtual[j])
            nei_virtual = np.concatenate((nei_virtual, nei_virtual_new_cell.reshape(1,)), axis=0)
            #dk
            #dk_virtual_new_cell = np.power(((1-dormant)*nei_virtual[j] + ni[j]) / nf_virtual[j], rk_virtual[j])

            if not dormant:
                dk_virtual_new_cell = np.power((nei_virtual[j] + ni[j]) / nf_virtual[j], rk_virtual[j])
            else:
                dk_virtual_new_cell = np.power(ni[j] / nf_virtual[j], rk_virtual[j])

            #print(f"{1-dormant} - {dk_virtual_new_cell}")
            dk_virtual = np.concatenate((dk_virtual, dk_virtual_new_cell.reshape(1,)), axis=0)

        ##print(f"ni\t\tsigma\t\t\t\tnf\t\t\trk\t\t\tnei\t\t\t\t\t\tdk")
        ##print(print(f"{ni[j]}\t{sigma[j]}\t{nf_virtual[j]}\t{rk_virtual[j]}\t{nei_virtual[j]}\t{dk_virtual[j]}"))
        #SAMPLED

        # nf
        if j == 0 or dormant:
            nf_sampled_new_cell = random.normal(normal_mean[j], normal_stdev[j], 1)
        #print(f"nf_sampled[{j}]: {np.absolute(nf_sampled_new_cell)}")
        nf_sampled = np.concatenate((nf_sampled,nf_sampled_new_cell), axis=0)
        #rk

        rk_sampled_new_cell = np.power(np.absolute(nf_sampled[j])/reference_number_of_cycles, k)
        rk_sampled = np.concatenate((rk_sampled, rk_sampled_new_cell.reshape(1,)), axis=0)
        #nf
        dk_sampled[0] = 0 #np.power(nei_sampled[0] / nf_sampled[0], rk_sampled[0])
        if j>0:
            #nei
            #print(f"nf_sampled[j]: {nf_sampled[j]}")
            nei_sampled_new_cell = nf_sampled[j]*np.power(dk_sampled[j-1],1/rk_sampled[j])
            nei_sampled = np.concatenate((nei_sampled, nei_sampled_new_cell.reshape(1,)), axis=0)
            #dk
            dk_sampled_new_cell = np.power(((1-dormant)*nei_sampled[j] + ni[j])/nf_sampled[j], rk_sampled[j])
            dk_sampled = np.concatenate((dk_sampled, dk_sampled_new_cell.reshape(1,)), axis=0)

        #print(f"j:{j}\t{dk_virtual_new_cell}\t{dk_sampled_new_cell}")


        #conditions
        c = dk_virtual[j]
        d = dk_sampled[j]
        #print(f"j:{j}\t{c}\t{d}")
        condition_1 = c < damage_level_limit
        condition_2 = ((damage_level_limit < c) & (c < 1))
        condition_3 = c > 1

        sub_condition_1 = d > 1
        sub_condition_2_1 = d > 1
        sub_condition_2_2 = d < 1
        sub_sub_condition_2_1_1 = d - 1 < c - damage_level_limit  # virtual happened sooner → preventive
        sub_sub_condition_2_1_2 = d - 1 > c - damage_level_limit  # sampled happened sooner → corrective
        sub_condition_3 = d > 1
        sub_sub_condition_3_1 = c > d
        sub_sub_condition_3_2 = c < d

        and_1 = condition_1*sub_condition_1
        and_2 = condition_2*sub_condition_2_1*sub_sub_condition_2_1_1
        and_3 = condition_2*sub_condition_2_1*sub_sub_condition_2_1_2
        and_4 = condition_2*sub_condition_2_2*sub_condition_2_2
        and_5 = condition_3*sub_condition_3*sub_sub_condition_3_1
        and_6 = condition_3*sub_condition_3*sub_sub_condition_3_2
        if and_1:
            failure_type = "Corrective1"
            print(failure_type)
            dormant = True
            corrective += 1

        elif and_2:
            failure_type = "Preventive1"
            print(failure_type)
            dormant = True
            preventive = preventive + 1

        elif and_3:
            failure_type = "Corrective2"
            print(failure_type)
            dormant = True
            corrective += 1

        elif and_4:
            failure_type = "Preventive2"
            print(failure_type)
            dormant = True
            preventive = preventive + 1

        elif and_5:
            failure_type = "Preventive3"
            print(failure_type)
            dormant = True
            preventive = preventive + 1

        elif and_6:
            failure_type = "Corrective3"
            print(failure_type)
            dormant = True
            corrective += 1

        else:
            dormant = False

        print(f"preventive: {preventive}({i})")
        #print(f"corrective: {corrective}")
        #print(f'j:{j}\t{preventive}')
    # preventive_array = np.concatenate((preventive_array, preventive), axis=0)
    # dormant = and_1 + and_2 + and_3 + and_4 + and_5 + and_6
    # print(f'i:{i}\t{preventive}')

   # def plot(var):
        #plt.plot(var)
        #plt.show()

    #plot(dk_virtual)
    #plot(dk_sampled)



corrective_average = corrective/number_of_iterations
preventive_average = float(preventive/number_of_iterations)
print(f"preventive_total: {preventive}")
print(f"number_of_iterations: {number_of_iterations}")
print(f"corrective_total: {corrective}")
print(f"preventive_average: {preventive_average}")


total_cost_increasing_120_140 = corrective_cost*corrective_average + preventive_cost*preventive_average


stop = timeit.default_timer()
print('Time: ', stop - start)

np.savez(f"total_cost_{damage_level_limit}_{ing}_{first_load}_{second_load}", total_cost_increasing_120_140)
np.savez(f"corrective_average_{damage_level_limit}_{ing}_{first_load}_{second_load}", corrective_average)
np.savez(f"preventive_average_{damage_level_limit}_{ing}_{first_load}_{second_load}", preventive_average)
np.savez(f"corrective_{damage_level_limit}_{ing}_{first_load}_{second_load}", corrective)
np.savez(f"preventive_{damage_level_limit}_{ing}_{first_load}_{second_load}", preventive)
