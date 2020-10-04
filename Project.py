"""
Group 2: Rokshar Abdul Bhisti, Kevin George, Nicole Hill

Instructions to running the model:
Choose which test case you want to run. The DATA FILE and the PRINT SECTION vary between models, but nothing else.
Selectively comment/uncomment the appropriate portions of the code according to which test case is active.
Run the model. 

"""

from pyomo.environ import*

model=AbstractModel()



#Sets
model.GEN=Set() #All generator models available

#Parameters
model.Cap=Param(model.GEN) #Capacity of each generator model
model.Cc=Param(model.GEN) #Fuel cost coefficient for each generator model 
model.Cf=Param(model.GEN) #Fixed cost for operation and maintenance
model.C=Param(model.GEN) #Investment cost coefficient
model.Cv=Param(model.GEN) #Variable cost coefficient
model.Dav=Param() #Average demand
model.Dmax=Param() #Maximum demand
model.n=Param() #Maximum number of generators available per array type, subjective
model.Cun=Param(model.GEN) #Unavailability cost coefficient

#Decision Variables
model.x=Var(model.GEN, within=NonNegativeIntegers) #How many generators of this model do we install?
model.y=Var(model.GEN, domain=Binary) #Do we install this generator array?
model.P=Var(model.GEN, within=NonNegativeReals) #Total power in the generator array
model.USP=Var(model.GEN, within=NonNegativeReals) #Average unserved power

#Objective Function: minimize cost
def objective (model):
    return (sum(model.x[i]*model.C[i] + model.Cc[i]*model.P[i] + model.Cf[i]*model.x[i] +model.Cv[i]*model.P[i] +model.Cun[i]*model.USP[i] for i in model.GEN))
model.minCost=Objective(rule=objective,sense=minimize)

#Constraints
#Meeting the average demand
def AvgD (model):
    return sum(model.P[i] for i in model.GEN)==model.Dav
model.MeetingAverageDemand=Constraint(rule=AvgD)

#Limit on power generation
def TotPower (model,i):
    return (model.P[i]<=model.Cap[i]*model.x[i])
model.PowerGen=Constraint(model.GEN, rule=TotPower)

#Minimum capacity for the generator array
def MinCap (model):
    return sum(model.Cap[i]*model.x[i] for i in model.GEN)>=model.Dmax
model.MeetingMaxDemand=Constraint(rule=MinCap)

#Connecting generators to generator array
def ArrayBound (model,i):
    return model.x[i]<=model.y[i]*model.n
model.KeepingItSimple=Constraint(model.GEN, rule=ArrayBound)

#Only one type of generator array can be chosen
def Highlander (model):
    return sum(model.y[i] for i in model.GEN)==1
model.OnlyOneType=Constraint(rule=Highlander)

#Defining USP
def BackUp (model,i):
    return ((model.Dmax+model.Cap[i])*model.y[i]-model.Cap[i]*model.x[i])<=model.USP[i]
model.Unavailable=Constraint(model.GEN, rule=BackUp)

#Running an abstract model
#Step 1: Combine data file and abstract model
data=DataPortal() #Pyomo object that knows how to feed the data file to the abstract model

#Data file for Test Case 1
data.load(filename="Project_Case_1.dat", model=model) #Loads the data file, strings are in quotes or it believes it's an object, model=model indicates that our models are named model

#Data file for Test Case 2
#data.load(filename="Project_Case_2.dat", model=model) #Loads the data file, strings are in quotes or it believes it's an object, model=model indicates that our models are named model

instance = model.create_instance(data) #Passes information from the data file loaded in previous step, creates a concrete model for us

#Step 2: Run the model!
#This is the stuff you need to do this in Spyder
optimizer = SolverFactory("glpk") #loading the solver into an object (optimizer here)
results = optimizer.solve(instance) #solves the model, stores some results into resulting object
instance.pprint() # prints out all model constraints



#Print results if the model ran without error
if(results.solver.status==SolverStatus.ok) and (results.solver.termination_condition==TerminationCondition.optimal):
    instance.display() #shows the solution
#Print Information for Test Case 1
    TotalPower=sum(instance.P[i]() for i in instance.GEN)
    Gen1=instance.x['GT35']()
    Gen2=instance.x['GT10']()
    Gen3=instance.x['PG5371']()
    Gen4=instance.x['PG6551']()
    CalculatedCost=instance.minCost()
    CalcInvestment=sum(instance.x[i]()*instance.C[i] for i in instance.GEN)
    CalcFuel=sum(instance.P[i]()*instance.Cc[i] for i in instance.GEN)
    CalcOM=sum(instance.Cf[i]*instance.x[i]()+instance.Cv[i]*instance.P[i]() for i in instance.GEN)
    CalcUn=sum(instance.Cun[i]*instance.USP[i]() for i in instance.GEN)

    print("The average power needed will be","%.2f"%TotalPower,"MW for the year.")
    print("The generators needed will be","%.0f"%Gen1,"GT35 generators,","%.0f"%Gen2,"GT10 generators,","%.0f"%Gen3,"PG5371 generators, and ","%.0f"%Gen4,"PG6551 generators.")
    print("If unavailability is included, the total cost will be $","%.2f"%CalculatedCost,"for the project generator array scheme. The total cost is broken into investment cost, $","%.2f"%CalcInvestment,", fuel cost, $","%.2f"%CalcFuel,", operations and maintenance cost, $","%.2f"%CalcOM,", and unavailability cost, $","%.2f"%CalcUn,".")

#Print Information for Test Case 2

#    TotalPower=sum(instance.P[i]() for i in instance.GEN)
#    Gen1=instance.x['PGT10']()
#    Gen2=instance.x['GT35']()
#    Gen3=instance.x['GT10']()
#    Gen4=instance.x['PG5371']()
#    CalculatedCost=instance.minCost()
#    CalcInvestment=sum(instance.x[i]()*instance.C[i] for i in instance.GEN)
#    CalcFuel=sum(instance.P[i]()*instance.Cc[i] for i in instance.GEN)
#    CalcOM=sum(instance.Cf[i]*instance.x[i]()+instance.Cv[i]*instance.P[i]() for i in instance.GEN)
#    CalcUn=sum(instance.Cun[i]*instance.USP[i]() for i in instance.GEN)
#    print("The average power needed will be","%.2f"%TotalPower,"MW for the year.")
#    print("The generators needed will be","%.0f"%Gen1,"PGT10 generators,","%.0f"%Gen2,"GT35 generators,","%.0f"%Gen3,"GT10 generators, and","%.0f"%Gen4,"PG5371 generators.")
#    print("If unavailability is included, the total cost will be $","%.2f"%CalculatedCost,"for the project generator array scheme. The total cost is broken into investment cost, $","%.2f"%CalcInvestment,", fuel cost, $","%.2f"%CalcFuel,", operations and maintenance cost, $","%.2f"%CalcOM,", and unavailability cost, $","%.2f"%CalcUn,".")




elif(results.solver.termination_condition==TerminationCondition.infeasible or results.solver.termination_condition == TerminationCondition.other):
    print("Model is INFEASIBLE. Consider removing/relaxing constraints")
#Catch-all idea that something 'other' happened, unspecified what
else:
    print("Solver Status: ",results.solver.status)
    print("Termination Condition", results.solver.termination_condition)