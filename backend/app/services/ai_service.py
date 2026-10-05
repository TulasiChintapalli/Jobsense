import os
import json
import re
import time

LISTS = [
    "technical_skills",
    "soft_skills",
    "education",
    "experience",
    "responsibilities",
    "keywords",
    "missing_skills",
    "recommended_skills",
]

PROMPT = """Analyze this job description.

Return ONLY valid JSON with these keys:

summary (string),
job_title (string),
company_name (string),
technical_skills (list),
soft_skills (list),
education (list),
experience (list),
responsibilities (list),
keywords (list),
missing_skills (list),
recommended_skills (list of objects with skill, reason, priority),
overall_score (integer from 0 to 100).

For recommended_skills, priority must be one of:
High, Medium, Low.

Use "Not specified" for unknown strings.
Use [] for unknown lists.
Do not invent facts.

JOB DESCRIPTION:
{jd}
"""


def analyze(text):
    """Analyze a job description using Gemini."""

    key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "")

    # Check Gemini configuration
    if (
        not key
        or key.startswith("your_")
        or not model
        or model.startswith("your_")
    ):
        return (
            None,
            "AI analysis is unavailable because the Gemini API key or model has not been configured."
        )

    try:
        from google import genai

        # Create Gemini client
        client = genai.Client(api_key=key)

        prompt = PROMPT.format(jd=text[:15000])

        # Try Gemini up to 3 times if it is temporarily unavailable
        response = None

        for attempt in range(3):

            try:
                print(
                    f"\n========== GEMINI ATTEMPT {attempt + 1}/3 =========="
                )
                print("Model:", model)

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                break

            except Exception as e:

                error_text = str(e)

                print("\n========== GEMINI REQUEST ERROR ==========")
                print(repr(e))
                print("==========================================\n")

                # Retry only temporary/unavailable errors
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "high demand" in error_text.lower()
                    or "overloaded" in error_text.lower()
                ):

                    if attempt < 2:
                        print(
                            "Gemini is temporarily busy. "
                            "Waiting 3 seconds before retry..."
                        )
                        time.sleep(3)
                        continue

                    return (
                        None,
                        "Gemini is temporarily busy after 3 attempts. Please try Analyze again."
                    )

                # Other errors should not be retried
                raise

        # Make sure Gemini returned a response
        if response is None:
            return (
                None,
                "Gemini did not return a response. Please try again."
            )

        # Show Gemini raw response
        print("\n========== GEMINI RAW RESPONSE ==========")
        print(repr(response.text))
        print("=========================================\n")

        if not response.text:
            raise ValueError(
                "Gemini returned an empty response."
            )

        # Remove Markdown code fences
        cleaned = response.text.strip()

        cleaned = re.sub(
            r"^```json\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"^```\s*",
            "",
            cleaned
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        cleaned = cleaned.strip()

        print("========== CLEANED JSON ==========")
        print(cleaned)
        print("==================================\n")

        # Convert JSON text to Python dictionary
        data = json.loads(cleaned)

        # Validate response
        result = _validate(data)

        return result, None

    except json.JSONDecodeError as e:

        print("\n========== JSON/PARSING ERROR ==========")
        print(repr(e))
        print("========================================\n")

        return (
            None,
            "The AI returned an invalid response. Please try again."
        )

    except (ValueError, KeyError, TypeError) as e:

        print("\n========== VALIDATION ERROR ==========")
        print(repr(e))
        print("=====================================\n")

        return (
            None,
            "The AI returned an invalid response. Please try again."
        )

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")
        print(repr(e))
        print("==================================\n")

        error_text = str(e)

        if (
            "401" in error_text
            or "403" in error_text
            or "API key" in error_text
            or "authentication" in error_text.lower()
        ):
            return (
                None,
                "Gemini API authentication failed. Please check your API key."
            )

        if (
            "404" in error_text
            or "NOT_FOUND" in error_text
        ):
            return (
                None,
                f"The Gemini model '{model}' was not found. Please check GEMINI_MODEL."
            )

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
        ):
            return (
                None,
                "Gemini API usage limit was reached. Please try again later."
            )

        return (
            None,
            "AI analysis failed. Please try again."
        )


def _validate(data):
    """Validate and normalize Gemini's response."""

    if not isinstance(data, dict):
        raise ValueError(
            "Gemini response is not a JSON object."
        )

    out = {
        "summary": str(
            data.get("summary") or "Not specified"
        )
    }

    for key in ("job_title", "company_name"):
        out[key] = str(
            data.get(key) or "Not specified"
        )

    # Lists
    for key in LISTS:

        value = data.get(key) or []

        if not isinstance(value, list):
            raise ValueError(
                f"{key} must be a list."
            )

        if key == "recommended_skills":
            out[key] = value
        else:
            out[key] = [
                str(item)
                for item in value
            ]

    # Recommended skills
    cleaned_recommendations = []

    for item in out["recommended_skills"]:

        if isinstance(item, dict):

            skill = str(
                item.get("skill") or "Not specified"
            )

            reason = str(
                item.get("reason") or ""
            )

            priority = str(
                item.get("priority") or "Medium"
            )

            if priority not in [
                "High",
                "Medium",
                "Low"
            ]:
                priority = "Medium"

            cleaned_recommendations.append({
                "skill": skill,
                "reason": reason,
                "priority": priority,
            })

        else:

            cleaned_recommendations.append({
                "skill": str(item),
                "reason": "",
                "priority": "Medium",
            })

    out["recommended_skills"] = cleaned_recommendations

    # Overall score
    try:
        score = int(
            data.get("overall_score") or 0
        )
    except (ValueError, TypeError):
        score = 0

    out["overall_score"] = max(
        0,
        min(100, score)
    )

    return out
