from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import asyncio

from github_fetch.schemas.schemas import  LLMResponseSchema, MetricSchema

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.5-flash-lite"

model_client = genai.Client(api_key=api_key)


async def generate_verdict_rank(metrics: MetricSchema) -> LLMResponseSchema:

    system_prompt = f""" 
    You are evaluating a software developer.

    Evaluate the developer's contributions to this repository
    using only the evidence provided below.

    Repository:
    id: {metrics.repo_id}
    Name: {metrics.repo_name}
    Description: {metrics.repo_description or "Not provided"}

    Metrics:
    Total repository commits: {metrics.total_commits}
    Developer commits: {metrics.user_total_commits}
    Active days: {metrics.user_active_days}

    Representative commit messages:
    {metrics.commit_messages}

    Instructions:
    1. Write a concise verdict of 2-3 sentences.
    2. Identify strengths supported by the available evidence.
    3. Identify limitations and uncertainties in the evidence.
    4. Score the developer's contributions on a scale of 1-10 (10 being the highest) based on the metrics and evidence provided.
    5. Do not invent skills, technologies, achievements, or responsibilities.
    6. Do not treat commit count alone as proof of developer quality.
    7. Return data matching the required response schema.
"""

    response = await model_client.aio.models.generate_content(
        model=MODEL,
        contents=system_prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=LLMResponseSchema,
        ),
    )
    if response.parsed is None:
        raise ValueError("Gemini did not return a valid structured evaluation")
    return LLMResponseSchema.model_validate(response.parsed)


async def add_metrics_and_sort(
    metrics: list[MetricSchema], max_concurrency=5
) -> list[MetricSchema]:

    llm_responses = []
    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_metric(metric):
        async with semaphore:
            llm_response = await generate_verdict_rank(metric)
            return llm_response

    results = await asyncio.gather(
        *[process_metric(metric) for metric in metrics], return_exceptions=True
    )
    llm_responses = [r for r in results if isinstance(r, LLMResponseSchema)]

    llm_response_map = {response.id: response for response in llm_responses}

    for metric in metrics:
        if metric.repo_id in llm_response_map:
            llm_response = llm_response_map[metric.repo_id]
            metric.llm_summary = f"{llm_response.verdict}\nStrengths: {llm_response.strengths}\nLimitations: {llm_response.limitations}"
            metric.llm_rank = llm_response.rank

    sorted_metrics = sorted(
        metrics, key=lambda m: m.llm_rank if m.llm_rank is not None else 0, reverse=True
    )

    return sorted_metrics
