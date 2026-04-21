import tiktoken

USD_TO_INR = 83.0

PRICING = {
    "image_input":       0.00025,
    "large_image_input": 0.001,
    "input_token":       0.75  / 1_000_000,
    "output_token":      4.50  / 1_000_000,
}


def calculate_image_cost(width: int, height: int) -> float:
    """Return cost for one image based on its dimensions."""
    return (
        PRICING["image_input"]
        if (width < 720 and height < 720)
        else PRICING["large_image_input"]
    )


def count_tokens(text: str) -> int:
    try:
        enc = tiktoken.encoding_for_model("gpt-5.4-mini")
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def calculate_token_costs(prompt: str, result_dict: dict) -> tuple[float, float, int, int]:
    """Returns (input_cost, output_cost, input_tokens, output_tokens)."""
    input_tokens  = count_tokens(prompt)
    output_tokens = count_tokens(str(result_dict))
    input_cost    = input_tokens  * PRICING["input_token"]
    output_cost   = output_tokens * PRICING["output_token"]
    return input_cost, output_cost, input_tokens, output_tokens


def calculate_total_cost(
    image_cost:        float,
    input_cost:        float,
    output_cost:       float,
    extra_token_costs: float = 0.0,
) -> tuple[float, float]:
    """Returns (total_cost_usd, total_cost_inr)."""
    total_usd = round(image_cost + input_cost + output_cost + extra_token_costs, 6)
    total_inr = round(total_usd * USD_TO_INR, 4)
    return total_usd, total_inr