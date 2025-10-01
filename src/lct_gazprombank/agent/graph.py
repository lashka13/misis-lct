"""Граф агента для классификации отзывов."""

from langgraph.graph import END, START, StateGraph

from lct_gazprombank.agent.prompts import (
    CLASSIFY_CATEGORY_MULTIPLE_REVIEWS_PROMPT,
    CLASSIFY_SENTIMENT_MULTIPLE_REVIEWS_PROMPT,
)
from lct_gazprombank.agent.state import ClassificationState
from lct_gazprombank.agent.utils import (
    format_reviews,
    format_reviews_with_categories,
    llm,
    parse_review_categories,
    parse_review_sentiments,
)


async def classify_category(state: ClassificationState) -> ClassificationState:
    """Классификация категорий для каждого отзыва

    Args:
        state (ClassificationState): Состояние агента

    Returns:
        ClassificationState: Обновленное состояние с категориями
    """
    reviews = state["reviews"]
    formatted_reviews = format_reviews(reviews)
    available_categories = state["available_categories"]
    formatted_available_categories = ", ".join(available_categories)

    prompt = CLASSIFY_CATEGORY_MULTIPLE_REVIEWS_PROMPT.format(
        reviews=formatted_reviews,
        available_categories=formatted_available_categories,
    )

    response = await llm.ainvoke(prompt)
    categories = parse_review_categories(response)

    return {"categories": categories}


async def classify_sentiments(state: ClassificationState) -> ClassificationState:
    """Классификация тональности для каждой категории в каждом отзыве

    Args:
        state (ClassificationState): Состояние агента

    Returns:
        ClassificationState: Обновленное состояние с тональностями
    """
    reviews = state["reviews"]
    categories = state["categories"]
    reviews_with_categories = format_reviews_with_categories(reviews, categories)

    prompt = CLASSIFY_SENTIMENT_MULTIPLE_REVIEWS_PROMPT.format(reviews_with_categories=reviews_with_categories)

    response = await llm.ainvoke(prompt)
    sentiments = parse_review_sentiments(response)

    return {"sentiments": sentiments}


workflow = StateGraph(ClassificationState)

workflow.add_node("classify_category", classify_category)
workflow.add_node("classify_sentiments", classify_sentiments)

workflow.add_edge(START, "classify_category")
workflow.add_edge("classify_category", "classify_sentiments")
workflow.add_edge("classify_sentiments", END)

classification_agent = workflow.compile()
