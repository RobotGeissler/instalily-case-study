# instalily-case-study

## Basic outline

I think so far it makes alot of sense to do a corrective agentic rag setup so the underlying information in response to tech prompts is as accurate as possible (minimizes hallucination, grounds in relevant information). (https://arxiv.org/pdf/2501.09136)

Progress update: going to bed for a few hours. Handshake is done but none of the steps below are finished technically. Deepseek will require a more detailed implementation. However, I am now positioned to finish them hopefully in short order and can use openai as a fall back.

## Steps (in order of priority)
1. Fix search to handle more than just part numbers
2. Export environment, DOCs
3. Container orchestration in docker to avoid compatibility issues
4. Edit react chat ui - Unnecessary
5. Populate retriever data - Difficult due to PartSelect bot detection
6. Integrate Corrective critic layer - Difficult due to PartSelect Bot detection

