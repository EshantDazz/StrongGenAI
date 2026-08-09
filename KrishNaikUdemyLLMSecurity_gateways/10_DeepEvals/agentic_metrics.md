- `Tool Correctness`: Just check if the right tool has been called
- `Argument Correctness`: If the argukent passed to the tools are correct or not
- `Task Completeness`: Whether the whole agent loop completed the task or not based on the user task or query.<br>
Example even if user asked to do a web search and we have received the answer from 
normal system context then also it should be mentioned as bad score

- `Step Efficiency`: If duplicate tool call or unnecessary multiple tool call are happening for the same query which might not be required. Even if the task is completed if it is done in an optimised mannner or not

- `Plan Adherence`: If there is a plan and towards the end it searches about things not related to the query and diverts away from the main topic that is calculated here. 