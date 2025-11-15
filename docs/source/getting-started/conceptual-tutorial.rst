===============================
Conceptual Tutorial
===============================

Before we build useful agentic AI applications using Osprey, it's important to
build a mental model of how Osprey and its applications work.

This conceptual tutorial will guide you through the key concepts of Osprey and
show you the way to think in Osprey, preparing your mind for the hands-on coding journey ahead.

How Osprey Works
================

Agentic AI application can be treated as chatbot with tools. Currently there are two major
types of agentic AI applications: ReAct agents and Planning agents.

.. tab-set::

   .. tab-item:: ReAct Agents

      ReAct agents work in a way that is similar to how LLMs handle chat history.
      When a user query comes in, the agent processes the entire conversation history,
      along with the previous tool usage records, to decide the next action.

      Advantage of ReAct agents is that they can leverage the full power of LLMs to
      dynamically decide what to do next based on the entire context. However, this
      also means that ReAct agents can be less efficient and less predictable, as
      they may revisit previous steps or make decisions that are hard to foresee.

   .. tab-item:: Planning Agents

      Planning agents, on the other hand, separate the "thinking" and "acting" phases.
      For every user query, they first create a comprehensive plan, breaking down
      the task into manageable steps. Once the plan is formulated, the agent
      executes each step sequentially, utilizing tools as necessary to accomplish
      each subtask.

      The advantage of Planning agents is that the execution path is more structured and predictable,
      as the plan is created upfront. This can lead to more efficient use of tools and resources.
      Also, planning agents are less dependencies on the LLM's ability to generate stable outputs
      since it decompose the task into smaller, easier steps, and each step can be
      handled with more focused prompts, and potentially smaller models.

      Osprey belongs to the Planning agents category. *That being said, you can still build
      ReAct agents using Osprey*, which we will cover in advanced tutorials later.

.. admonition:: Potential Edits
   :class: warning

   Talk more about nodes, states, states manager, classifier, and orchestrator in Osprey?

In Osprey world, tools are called **Capabilities**. Given a user query, Osprey core
would decide which capabilities to use, in what order, and with what inputs. In other words,
Osprey chains capabilities together to accomplish complex tasks.

The information that pass between the capabilities are wrapped in formatted data classes called **Contexts**.
It's strictly formatted to mitigate the risk of LLMs "hallucinating" or misinterpreting the data.

Capabilities and contexts are the central building blocks of Osprey applications. So when design your
Osprey application, always think in terms of capabilities and contexts:

- What capabilities do I need to accomplish the task?
- What contexts would the capability need to work?
- What contexts should the capability produce as output?

Now let's look at a simple example (which we will implement in :doc:`hello-world-tutorial` later)
to better understand those concepts.

Mindflow to Build a Weather Assistant in Osprey
===============================================

Assuming we want to build a weather assistant that can provide weather information based on user queries.

What would users ask
--------------------

First step is to think about what queries we want to support, or we imagine users would ask. Based on our
experience in real life, for the weather assistant, users would typically ask questions like:

- "What's the weather like in San Francisco today?"
- "Will it rain tomorrow in New York?"
- "Give me a 5-day weather forecast for Los Angeles."

Plus some tricky ones that can happen in a chat:

- "What about the day after tomorrow?" -- referring to previous query
- "Can you tell me a joke about the weather?" -- out of scope query

What capabilities are needed
----------------------------

To deal with the queries above, obviously we need a capabilities that can fetch weather data,
given the location and date. Let's call it `FetchWeatherCapability`.
This capability would require the location and date as inputs, and return the weather information.
Therefore we'll need the following contexts:

- `LocationContext` -- to represent the location information
- `DateContext` -- to represent the date information
- `WeatherContext` -- to represent the weather information returned by the capability

Of course, we can combine the LocationContext and DateContext into a single `WeatherQueryContext` if we want to.
That choice depends on how we want to structure our data and our personal preference.

Then how can we handle the tricky queries like "Can you tell me a joke about the weather?"?
Osprey provides a build-in mechanism to route out-of-scope queries to a clarify node [#explain-node]_ -- if
Osprey doesn't know how to make a plan based on available capabilities, it would ask the user for clarification.

To handle it more humanly, we can create a `ConversationCapability` that chats with users
for those queries that don't require tool usage. One tricky thing here is that this conversation capability
doesn't need any context as input, also it doesn't produce any context as output -- it's like
an isolated node that won't be chained with other capabilities. You may ask that then how can we get the user query,
if the capability doesn't take any context as input? The answer is that Osprey always provide
the original and processed user query to all capabilities through the state manager and step stores. Similarly,
each capability has a way to summarize its execution result, so that even though it doesn't produce any context as output,
Osprey would know what to return to user in the respond node [#explain-node]_.

.. admonition:: Potential Edits
   :class: warning

   Talk more about what stores in steps and state manager here?

Are those capabilities sufficient? Maybe not. To think more carefully with what we have so far: how can we get the
`LocationContext` and `DateContext` from user queries? It could be easy if the user query is straightforward, but
what if the user query looks like:

- "What's the weather like in NYC?"
- "Will it rain tonight around Stanford university?"

So we probably need another capability to extract location and date information from user queries:

- `ExtractLocationCapability` -- to extract location information from user queries
- `ExtractDateCapability` -- to extract date information from user queries

As explained previously, those two capabilities don't need any context as input, since they can get the user query
from the state manager. And obviously, they would produce `LocationContext` and `DateContext` respectively.

Repeat the Loop
---------------

Now you should get a basic idea of how to think in Osprey when we design our application:

1. What capabilities are needed?
2. What contexts are needed for each capability?
3. How to get those contexts?
    * The contexts are straightforward to get from user queries -- no more capabilities needed
    * Otherwise -- need extra capabilities to produce them
4. Repeat step 1-3 until no more capabilities are needed

.. admonition:: Questions
   :class: error

   Would the orchestrator be able to create simple contexts directly?

Here is one design for the weather assistant based on the above analysis:

.. tab-set::

   .. tab-item:: Capabilities

      - FetchWeatherCapability

        Call weather API to fetch weather information based on location and date.

        - Requires: LocationContext, DateContext
        - Provides: WeatherContext

      ----

      - ExtractLocationCapability

        Parse location information from user queries.

        - Requires: None
        - Provides: LocationContext

      ----

      - ExtractDateCapability

        Parse date information from user queries.

        - Requires: None
        - Provides: DateContext

      ----

      - ConversationCapability

        Provide chat capability for out-of-scope queries.

        - Requires: None
        - Provides: None

   .. tab-item:: Contexts

      - LocationContext
      - DateContext
      - WeatherContext

Tell Osprey Where to find/How to Use Capabilities
-------------------------------------------------

After creating all the necessary capabilities and contexts, the final step is
to tell Osprey how to use those capabilities to accomplish user queries.
This is done by providing guidelines in each capabilities.

Now the capabilities and contexts are ready -- you'll call Osprey's registry to
register those stuff so that Osprey knows they exist/where to find them.

.. admonition:: Content Request
   :class: error

   Should provide some concrete guideline examples?

   Also more details on Osprey registry?

Example Plan from Weather Assistant
-----------------------------------

.. admonition:: Content Request
   :class: error

   Show sample plans for several typical queries in weather assistant.

Advanced Topics
===============

"Smart" capability vs "dumb" capability
---------------------------------------

Smart capabilities are those that make use of LLMs, while dumb capabilities are those that
perform deterministic operations without LLMs. In Osprey, it's generally recommended to
keep capabilities as "dumb" as possible, pushing the "smart" logic to the orchestrator level.

.. admonition:: Content Request
   :class: error

   More advanced topics/tricks that would help users build better mental model of Osprey?

.. [#explain-node] Here we need to explain or link to the node concept in Osprey.
