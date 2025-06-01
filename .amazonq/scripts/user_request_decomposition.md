# User Request Decomposition Framework

## Purpose
Transform complex user requests into clear, actionable steps by systematically breaking down the task into its core components.

### Analysis Process
1. Identify Core Objectives

Extract the primary goal(s) from the request
Distinguish between main objectives and supporting requirements
Flag any implicit assumptions or unstated needs

2. Map Dependencies

Determine which steps must occur in sequence
Identify parallel tasks that can happen simultaneously
Note any prerequisites or constraints

3. Define Atomic Actions

Break each objective into the smallest meaningful units
Ensure each step has a clear input and output
Verify that no step combines multiple distinct operations

4. Structure the Sequence

Order steps by logical flow and dependencies
Group related actions into phases if applicable
Build in checkpoints for validation or decision points

5. Specify Success Criteria

Define what "done" looks like for each step
Include measurable outcomes where possible
Note any quality standards or acceptance criteria

## Output Format
### Present the decomposed request as:

Goal Statement: One-sentence summary of the end objective
Prerequisites: Any required context, tools, or information
Step-by-Step Process: Numbered list with:

Action verb + specific task
Expected output/result
Dependencies (if any)


Validation: How to verify successful completion

## Example Application
Original Request: "Help me analyze customer feedback and create a presentation for executives"
Decomposed:

Goal: Create executive presentation summarizing customer feedback insights
Prerequisites: Access to feedback data, presentation software
Steps:

Collect all customer feedback from specified sources
Categorize feedback by theme (product, service, pricing)
Quantify frequency and sentiment for each category
Identify top 3-5 actionable insights
Design presentation structure (problem, data, recommendations)
Create visual representations of key data
Draft executive summary slide
Review and refine for clarity and impact


Validation: Presentation answers "What do customers want?" with data-backed recommendations

# Execution
Now run this, step-by-step, on the user's request. After you run this script, ask the user if they would like you to follow the actions as specified.
