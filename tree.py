#tree.py
#Author: Thomas McNulty
#Class: Comp131
#Construct a behavior tree using the nodes.
#All nodes require a name given as the first parameter. Class declarations
#are in nodes.py


from nodes import *
from numpy.random import choice 



#Battery check sequence
bat_check = less_than_condition("BATTERY", "BATTERY_LEVEL", 30)
find_home = task("FIND HOME", 2, .1)
go_home = task("GO HOME", 3, 0)
dock = task("DOCK", 2, 0)
bat_sequence = sequence("BAT SEQUENCE", bat_check, find_home, go_home, dock)


#Spot check sequence
spot = condition("SPOT", "SPOT_CLEANING")
clean_spot = task("CLEAN SPOT", 3, 0)
spot_timer = timer("SPOT TIMER", 20, clean_spot)
done_spot = done_spot("DONE SPOT", 2, 0)
spot_sequence = sequence("SPOT SEQUENCE", spot, spot_timer, done_spot)



general_cleaning = condition("GENERAL CLEANING", "GENERAL_CLEANING")


#Second spot check sequence inside general cleaning
dusty_spot = condition("DUSTY SPOT", "DUSTY_SPOT")
clean_spot2 = task("CLEAN SPOT 2", 1, 0)
spot_timer = timer("SPOT TIMER", 35, clean_spot2)
general_spot_sequence = sequence("SPOT SEQUENCE", dusty_spot, spot_timer)


clean_floor = task("CLEAN FLOOR", 2, .1)
until_success_floor = until_success("UNTIL SUCCESS FLOOR", clean_floor)


spot_priority = priority("SPOT PRIORITY", general_spot_sequence, until_success_floor)
done_general = done_general("DONE GENERAL", 1, 0)
cleaning_sequence = sequence("CLEANING SEQUENCE", spot_priority, done_general)

general_sequence = sequence("GENERAL SEQUENCE", general_cleaning, cleaning_sequence)

main_selector = selector("MAIN SELECTOR", spot_sequence, general_sequence)


do_nothing = task("DO NOTHING", 1, 0)


#First node
main_priority = priority("MAIN PRIORITY", bat_sequence, main_selector, do_nothing)


#Main function. Has inout for blackboard conditions and requests for evaluations
def main(first_node):

    __updateBlackboard()

    evaluations = int(input("How many evaluations?: "))
    while evaluations != 0:

        for i in range(evaluations):
            status = first_node.run()
  
        evaluations = int(input("How many more evaluations?: "))
        if evaluations > 0 and input("Any changes (y or n): ").lower() == "y":
            __updateBlackboard()


    print("Tree concluded")



def __updateBlackboard():
    blackboard["BATTERY_LEVEL"] = int(input("Starting battery level?: "))
    spotInput = input("Spot cleaning? (T or F): ")
    if spotInput.lower() == "t":
        blackboard["SPOT_CLEANING"] = True
    else:
        blackboard["SPOT_CLEANING"] = False

    generalInput = input("General cleaning? (T or F): ")
    if generalInput.lower() == "t":
        blackboard["GENERAL_CLEANING"] = True
    else:
        blackboard["GENERAL_CLEANING"] = False

    
if __name__ == "__main__":
    main(main_priority)