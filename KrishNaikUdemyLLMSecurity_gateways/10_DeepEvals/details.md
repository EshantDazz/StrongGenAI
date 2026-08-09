- Step0
If you dont have golden data set then you need to use a AI synthesizer to create 
results which needs to be used later for evaluation

- Step1

Data Curation (Create the dataset with all the goldens)

- Step2

Metrics Selection and Validation
Validation happens with keeping a human and taking the Evaluation of LLMas a Judge and make a
balance out of it

- Step3

Execution and TraceCapture

- Step4

Aumated Metric Evaluation
Apply metrics, check what each metric produces, compare it with a threashold\

- Step5
Automate this in CI/CD
If a particular threshold is not coming then we block the deployment

- Step6
Production Monitoring and FeedbackLoop



## Types of Evaluation
- G-Eval(Generation Evaluation)

Define the evaluation steps in Natural Language + Optional rubric 
We use LLM Holistic COT
Final Score + REasoning






- DAG (Deep Agentic Graph)
Define the Criterals in the form of graph
Node Based Calculation Happens

- QAG (Question Answer Generation)
Here we need ground Truth
Preset Questions
LLM gives three output yes / no/ IDK
based on yes/no/idk we do mathematical aggregation 
