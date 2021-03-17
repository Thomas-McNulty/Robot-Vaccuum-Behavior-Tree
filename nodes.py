#nodes.py
#Author: Thomas McNulty
#Class: Comp131
#Construct a behavior tree using the nodes.
#Various nodes used in the behavior tree
#Failure, Success, and Running represented as
#True False and None


from blackboard import blackboard
from numpy.random import choice 
import random


#Basic node class. Requires just a name.
#Input: Name
class basic_node():
    def __init__(self, name):
        self.name = name        



#Node with children class. Used as a parent class in many
#nodes. All parameters after name are added to the nodes
#children
#Input: Name, children in order
class multi_child_node(basic_node):
    def __init__(self, name, *children):
        super().__init__(name)
        self.children = []
        for child in children:
            self.children.append(child)




#Sequence node runs each of its children. If one of the children is
#running then it returns running and will reevaluate the child on the
#next iteration. Otherwise, this node succedes if no nodes fail from left to
#right, otherwise it fails.
#Input: Name, children in order (#1 first, #2 second...)
class sequence(multi_child_node):
    def run(self):

        #These two cases do essentially the same thing, however the first
        #will skip children until the running node is found. This is
        #known because the sequence itself will have been marked running in
        #the last iteration.
        if self.name in blackboard:
            found_running = False
            for child in self.children:

                #Once first running is found, the rest of the
                #nodes are evaluated
                if found_running or child.name in blackboard:
                    found_running = True
                    status = child.run()


                    #Removes self from blackboard if terminated
                    if status == False:
                        del blackboard[self.name]
                        return False

                    if status == None:
                        child_value = blackboard[child.name]
                        blackboard[self.name] = child_value
                        return None

            del blackboard[self.name]

        else:
            for child in self.children:
                status = child.run()

                if status == False:
                    return False
                if status == None:
                    child_value = blackboard[child.name]
                    blackboard[self.name] = child_value
                    return None

        return True



#Selector node runs each of its children. If one of the children is
#running then it returns running and will reevaluate the child on the
#next iteration. Otherwise, this node succedes if one node succedes from left to
#right, otherwise it fails.
#Input: Name, children in order (#1 first, #2 second...)
class selector(multi_child_node):

    def run(self):


        #These two cases do essentially the same thing, however the first
        #will skip children until the running node is found. This is
        #known because the sequence itself will have been marked running in
        #the last iteration.
        if self.name in blackboard:
            found_running = False
            for child in self.children:
                if found_running or child.name in blackboard:
                    found_running = True
                    status = child.run()

                    #Removes self from blackboard if terminated
                    if status == True:
                        del blackboard[self.name]
                        return True

                    if status == None:
                        child_value = blackboard[child.name]
                        blackboard[self.name] = child_value
                        return None

            del blackboard[self.name]
                


        else:
            for child in self.children:
                status = child.run()

                if status == True:
                    return True
                if status == None:
                    child_value = blackboard[child.name]
                    blackboard[self.name] = child_value
                    return None

        return False



#Priority node has multiple children. Priority is based on left to
#right input. This node evaulates its children with no reguard for running.
#Success conditions are the same for priority as for selector.
#Input: Name, children in priority order (#1 first, #2 second...)
class priority(multi_child_node):
    def run(self):

        for child in self.children:
            status = child.run()
            if status == True:
                if self.name in blackboard:
                    del blackboard[self.name]
                return True
            if status == None:
                child_value = blackboard[child.name]
                blackboard[self.name] = child_value
                return None

        if self.name in blackboard:
            del blackboard[self.name]

        return False




#This node runs until the child returns True. It does this by updating
#The blackboard at its name with some number so it is interprited as
#running. Once true is returned from the child it returns true.
#Input: Name, one child
class until_success(multi_child_node):

    def run(self):
        status = self.children[0].run()
        self.__printStatus(self.children[0].name, status)
        if status == False:
            blackboard[self.name] = 1
            return None

        #Sets child time to own time
        if status == None:
            child_value = blackboard[self.children[0].name]
            blackboard[self.name] = child_value
            return None

        #Removes self from blackboard if child nolonger running
        if self.name in blackboard:
            del blackboard[self.name]

        return True

    def __printStatus(self, name, status):
        if status == None:
            print(name + " RUNNING")
        elif status == False:
            print(name + " FAILED")
        elif status == True:
            print(name + " SUCCEDED")


#Timer accepts a time and a child. This node returns running until
#the time specified has been reached. Time is decremented only if the child
#returns true or false, running does not decrement the timer. This seemed
#intuitive because otheriwse a timer could loop infinately if the node time
#does not divide evenly into the timer time.
#Input: Name, tine, children in order (#1 first, #2 second...)
class timer(multi_child_node):

    def __init__(self, name, time, *children):
        super().__init__(name, *children)
        self.time = time


    def run(self):

        #If already running timer
        if self.name in blackboard:
            if blackboard[self.name] > 0:

                status = self.children[0].run()
                if status == None:
                    return None

                blackboard[self.name] -= 1
                return None

            status = self.children[0].run()

            if status == None:
                return None
            
            del blackboard[self.name]
            return status


        #Add new timer
        blackboard[self.name] = self.time
        status = self.children[0].run()


        if status == None:
            return None

        blackboard[self.name] -= 1
        return None



#Condition checks a property (prop) in the blackboard,
#it returns the boolean assumed to be held in the blackboard
#at the property. This node cannot return running.
#Input: name, property to check
class condition(basic_node):

    def __init__(self, name, prop):
        super().__init__(name)
        self.property = prop
    
    def run(self):
        status = blackboard[self.property]
        if status == True:
            print(self.name + " SUCCEDED")
        else:
            print(self.name + " FAILED")

        return status
    

#This condition inherits the standard condition, but uses an additional
#threshold parameter. This node checks if the blackboard property
#is less than treshold provided, returning true if it is so.
#Input: name, property to check, threshold to alert at
class less_than_condition(condition):

    def __init__(self, name, prop, threshold):
        super().__init__(name, prop)
        self.threshold = threshold
    
    def run(self):
        if blackboard[self.property] < self.threshold:
            print(self.name + " SUCCEDED")
            return True

        print(self.name + " FAILED")
        return False
    


#The standard task node requires a time of execution. The node will
#return running until the time specified has elapsed. The node must
#be evaluated for its timer to be decremented. 
#Input: name, time for running, Failure percentage (from 0 to 1)
class task(basic_node):
    
    def __init__(self, name, time, failure_percentage):
        super().__init__(name)
        self.time = time
        self.failure_percentage = failure_percentage


    def run(self):


        blackboard["BATTERY_LEVEL"]-=1
        
        #If the node is already running
        if self.name in blackboard:

            #If there is more time, time is reduced by 1
            if blackboard[self.name] > 0:
                blackboard[self.name] -= 1
                print(self.name + " RUNNING")
                return None

            #Otherwise the node is finished
            del blackboard[self.name]


            #Chooses random t/f value using failure percentage
            outcome = choice([True, False], 1, p=[1 - self.failure_percentage, self.failure_percentage])[0]
            if outcome == True:
                print(self.name + " SUCCEDED") 
            elif outcome == False:
                print(self.name + " FAILED") 

            return outcome



        #Initialize new timer if not in blackboard yet
        blackboard[self.name] = self.time - 1
        if blackboard[self.name] >= 0:
            print(self.name + " RUNNING")
            return None

        #Case where time was less than 1
        del blackboard[self.name]


        #Chooses random t/f value using failure percentage
        outcome = choice([True, False], 1, p=[1 - self.failure_percentage, self.failure_percentage])[0]
        if outcome == True:
            print(self.name + " SUCCEDED") 
        elif outcome == False:
            print(self.name + " FAILED") 

        return outcome



#This task inherits the standard task. It performs the generic
#Task run function, but additionally sets GENERAL_CLEANING in the blackboard
#to False.
#Input: name, time for running, Failure percentage (from 0 to 1)
class done_general(task):

    def run(self):

        result = super().run()

        if result == True:
            blackboard["GENERAL_CLEANING"] = False

        return result
    

#This task inherits the standard task. It performs the generic
#Task run function, but additionally sets DUSTY_SPOT in the blackboard
#to False.
#Input: name, time for running, Failure percentage (from 0 to 1)
class done_spot(task):

    def run(self):

        result = super().run()

        if result == True:
            blackboard["DUSTY_SPOT"] = False

        return result
    
