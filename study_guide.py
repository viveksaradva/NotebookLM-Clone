from typing import TypedDict, List
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph
from langchain.schema.runnable import RunnableLambda
from langchain_groq import ChatGroq

# Define state
class SummarizationState(TypedDict):
    chunk: str
    summary: str

# Initialize LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=1)

# Node function for summarizing a single chunk
def summarize_node(state: SummarizationState) -> SummarizationState:
    prompt = f"""
    You are an expert academic summarizer helping students quickly understand complex material. 
    Your task is to summarize the following text chunk clearly and concisely in 2–3 sentences.

    Follow these principles:
    - Focus only on the **core concepts**, **key points**, and **essential arguments**
    - Keep the original **intent**, but **simplify the language** to aid understanding
    - Remove repetition, tangents, or overly detailed explanations
    - If a definition, statistic, or example is central, include it briefly
    - Structure your summary logically so it flows and stands on its own

    Text:
    {state['chunk']}
    """
    response = llm([HumanMessage(content=prompt)])
    return {**state, "summary": response.content.strip()}

# Graph setup
summarize_graph_builder = StateGraph(SummarizationState)
summarize_graph_builder.add_node("summarize", RunnableLambda(summarize_node))
summarize_graph_builder.set_entry_point("summarize")
summarize_graph_builder.set_finish_point("summarize")
summarization_graph = summarize_graph_builder.compile()

# Function for external use
def summarize_chunks(chunks: List[str]) -> List[str]:
    summaries = []
    for chunk in chunks:
        result = summarization_graph.invoke({"chunk": chunk})
        summaries.append(result["summary"])
    return summaries



class GuideState(TypedDict):
    chunk: str  # now this holds the full document summary
    summary: str
    concept: str
    question: str
    analogy: str
    faq: str
    study_guide: str

# Reusing the same LLM
# def concept_node(state: GuideState) -> GuideState:
#     prompt = f"""Extract key concepts from this summary:\n{state['chunk']}"""
#     response = llm([HumanMessage(content=prompt)])
#     return {**state, "concept": response.content.strip()}
def concept_node(state: GuideState) -> GuideState:
    prompt = f"""
    You are an expert knowledge mapper. Extract and explain the key concepts from the following academic text chunk.

    Follow these guidelines:
    - Identify the most important concepts, principles, theories, or terms.
    - For each concept:
      - Provide a clear, concise definition.
      - Explain its role or importance in the topic.
      - Mention any relationships with other concepts (e.g., cause-effect, hierarchy).
      - Include formulas, models, or frameworks if discussed.
      - If there are debates or alternative views, mention them briefly.
    - Format: Use headings for each concept followed by a short explanation (2–4 sentences).

    Text:
    {state['chunk']}

    Output: A structured list of key concepts with clear explanations.
    """ 
    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        **state,
        "concept": response.content.strip()
    }


# def review_question_node(state: GuideState) -> GuideState:
#     prompt = f"""Create review questions from this summary:\n{state['chunk']}"""
#     response = llm([HumanMessage(content=prompt)])
#     return {**state, "question": response.content.strip()}
def review_question_node(state: GuideState) -> GuideState:
    prompt = f"""
    You are an expert educational assessment designer. Create thoughtful review questions based on the following academic text chunk.

    Guidelines:
    - Generate 3 to 5 questions that test understanding of core ideas and concepts
    - Use a variety of question types:
    - Recall (basic understanding)
    - Application (using ideas in new contexts)
    - Analysis (exploring relationships between concepts)
    - Evaluation (critical thinking or critique)
    - Each question should be clear, focused, and meaningful
    - For every question, provide a detailed answer explanation
    - Avoid yes/no or overly simplistic questions
    - Encourage deeper learning and reflection

    Text:
    {state["chunk"]}

    Output: A list of review questions with comprehensive answer explanations.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        **state,
        "question": response.content.strip()
    }

# def analogy_node(state: GuideState) -> GuideState:
#     prompt = f"""Generate helpful analogies for concepts in this summary:\n{state['chunk']}"""
#     response = llm([HumanMessage(content=prompt)])
#     return {**state, "analogy": response.content.strip()}
def analogy_node(state: GuideState) -> GuideState:
    prompt = f"""
    You are an expert in making complex concepts accessible. Create illuminating analogies for the key concepts in the provided text chunk.

    Follow these guidelines:
    - Identify 2-3 challenging or abstract concepts from the text
    - For each concept, create an analogy that:
    * Uses familiar, everyday scenarios or objects
    * Accurately represents the key relationships or properties of the concept
    * Helps bridge the gap between the unfamiliar and the familiar
    - Explain how the analogy maps to the original concept
    - Note any limitations of the analogy (where it breaks down)
    - Ensure analogies are culturally inclusive and widely accessible
    - When possible, use diverse domains for analogies (e.g., sports, cooking, nature)

    Input:
    {state["chunk"]}

    Output: Helpful analogies that make complex concepts more intuitive and memorable.
    """
 
    response = llm.invoke([HumanMessage(content=prompt)])
    return {
            **state,
            "analogy": response.content.strip()
        } 
# def FAQs_node(state: GuideState) -> GuideState:
#     prompt = f"""Create an FAQ section for this content:\n{state['chunk']}"""
#     response = llm([HumanMessage(content=prompt)])
#     return {**state, "faq": response.content.strip()}
def FAQs_node(state: GuideState) -> GuideState:
    prompt = f"""
    You are an expert educational content developer who specializes in creating helpful FAQ sections. Generate a comprehensive FAQ section based on the provided text chunk that resembles those found in high-quality reference books.

    Follow these guidelines:
    - Identify 4-6 questions that students or readers genuinely struggle with when learning this material
    - Create questions that:
    * Address common misconceptions or points of confusion
    * Cover practical applications of theoretical concepts
    * Clarify boundaries between similar or easily confused concepts
    * Address "why" questions that explain underlying principles or rationale
    * Include questions about exceptions to rules or special cases
    - Format questions as natural, conversational inquiries a student might actually ask
    - Craft detailed, clear answers that:
    * Directly address the core confusion
    * Provide illuminating examples where helpful
    * Reference specific sections or content from the original material
    * Anticipate and address follow-up questions
    - Include at least one question that addresses how this content connects to broader themes or topics
    - Ensure the FAQ section feels like a genuine resource, not a quiz or assessment

    Input: {state["chunk"]}

    Output: An authentic FAQ section that addresses real learning challenges with thoughtful, illuminating responses.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        **state,
        "faq": response.content.strip()
    }

# def integrative_guide_node(state: GuideState) -> GuideState:
#     prompt = f"""
#     Build a personalized study guide from:
#     Concepts: {state["concept"]}
#     Questions: {state["question"]}
#     Analogies: {state["analogy"]}
#     FAQs: {state["faq"]}
#     """
#     response = llm([HumanMessage(content=prompt)])
#     return {**state, "study_guide": response.content.strip()}
def integrative_guide_node(state: GuideState) -> GuideState:
    prompt = f"""
    You are an expert educational consultant designing personalized study plans. Integrate the information from the document chunks to create an optimal, intelligent study guide.

    Follow these guidelines:
    - Review all information from the summarization, concept mapping, review questions, and analogies
    - Create a cohesive study plan that:
    * Presents a logical learning progression from foundational to advanced concepts
    * Identifies the 3-5 most critical areas to focus on based on complexity and importance
    * Suggests specific study techniques suited to the material (e.g., spaced repetition, concept mapping)
    * Recommends time allocation for different topics based on difficulty and significance
    - Include metacognitive prompts that encourage the student to reflect on their understanding
    - Suggest connections to prior knowledge or related fields when relevant
    - Provide a brief "quick reference" section for essential formulas, definitions, or principles
    - Adapt language and approach based on apparent complexity of the material

    Input:
    Concepts:
    {state["concept"]}

    Review Questions:
    {state["question"]}

    Analogies:
    {state["analogy"]}

    FAQs:
    {state["faq"]}
    Output: A personalized, intelligent study guide that maximizes understanding and retention while being genuinely helpful and accessible.
    """
 
    response = llm.invoke([HumanMessage(content=prompt)])
    return {
        **state,
        "study_guide": response.content.strip()
    }
# Create the graph
guide_builder = StateGraph(GuideState)
guide_builder.add_node("extract_concepts_node", RunnableLambda(concept_node))
guide_builder.add_node("generate_review_qs_node", RunnableLambda(review_question_node))
guide_builder.add_node("generate_analogies_node", RunnableLambda(analogy_node))
guide_builder.add_node("build_FAQs_node", RunnableLambda(FAQs_node))
guide_builder.add_node("build_study_guide_node", RunnableLambda(integrative_guide_node))

guide_builder.set_entry_point("extract_concepts_node")
guide_builder.add_edge("extract_concepts_node", "generate_review_qs_node")
guide_builder.add_edge("generate_review_qs_node", "generate_analogies_node")
guide_builder.add_edge("generate_analogies_node", "build_FAQs_node")
guide_builder.add_edge("build_FAQs_node", "build_study_guide_node")
guide_builder.set_finish_point("build_study_guide_node")

study_guide_graph = guide_builder.compile()

# Function for external use
def generate_study_guide(document_summary: str) -> dict:
    initial_state = {"chunk": document_summary}
    return study_guide_graph.invoke(initial_state)


def full_study_pipeline(chunks: List[str]) -> dict:
    print("🔍 Summarizing chunks...")
    summaries = summarize_chunks(chunks)

    print("📘 Combining summaries...")
    combined_summary = "\n".join(summaries)

    print("🎯 Generating final study guide...")
    final_guide = generate_study_guide(combined_summary)
    
    return final_guide


test_chunk = """
Quantum entanglement is a physical phenomenon that occurs when pairs or groups of particles interact
in ways such that the quantum state of each particle cannot be described independently of the state of the others.
"""
from backend.vectordb.chroma_db import ChromaDBManager
vector_db = ChromaDBManager()
chunks = vector_db.get_documents("3318e72a")

# Test summarization
from pprint import pprint

# single_summary = summarize_chunks([chunks])
pprint(full_study_pipeline(test_chunk))
